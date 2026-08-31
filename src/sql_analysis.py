import sqlite3
from pathlib import Path

import pandas as pd


project_root = Path(__file__).resolve().parents[1]

database_path = project_root / "data" / "financial_data.db"


connection = sqlite3.connect(database_path)


# Query 1: Join company information with financial data
query = """
SELECT
    c.company_name,
    c.ticker,
    c.industry,
    c.currency,
    f.fiscal_year_end,
    f.revenue,
    f.operating_income,
    f.net_income,
    f.total_assets,
    f.total_liabilities,
    f.cash,
    f.operating_cash_flow
FROM financials AS f
JOIN companies AS c
    ON f.company_id = c.company_id
ORDER BY
    c.company_name,
    f.fiscal_year_end;
"""


financial_data = pd.read_sql_query(
    query,
    connection
)


print("\nALL COMPANY FINANCIAL DATA")
print(financial_data.to_string(index=False))


# Query 2: Calculate normalized financial metrics

ratio_query = """
SELECT
    c.company_name,
    c.ticker,
    f.fiscal_year_end,

    ROUND(
        100.0 * f.operating_income / f.revenue,
        2
    ) AS operating_margin_pct,

    ROUND(
        100.0 * f.net_income / f.revenue,
        2
    ) AS net_margin_pct,

    ROUND(
        100.0 * f.total_liabilities / f.total_assets,
        2
    ) AS liabilities_to_assets_pct,

    ROUND(
        100.0 * f.operating_cash_flow / f.revenue,
        2
    ) AS operating_cash_flow_margin_pct

FROM financials AS f

JOIN companies AS c
    ON f.company_id = c.company_id

ORDER BY
    c.company_name,
    f.fiscal_year_end;
"""


ratio_data = pd.read_sql_query(
    ratio_query,
    connection
)


print("\nFINANCIAL RATIOS FROM SQL")
print(ratio_data.to_string(index=False))



# Query 3: Calculate year-over-year revenue growth

growth_query = """
WITH revenue_history AS (
    SELECT
        c.company_name,
        c.ticker,
        f.fiscal_year_end,
        f.revenue,

        LAG(f.revenue) OVER (
            PARTITION BY c.company_id
            ORDER BY f.fiscal_year_end
        ) AS previous_revenue

    FROM financials AS f

    JOIN companies AS c
        ON f.company_id = c.company_id
)

SELECT
    company_name,
    ticker,
    fiscal_year_end,
    revenue,

    ROUND(
        100.0 * (revenue - previous_revenue)
        / previous_revenue,
        2
    ) AS revenue_growth_pct

FROM revenue_history

ORDER BY
    company_name,
    fiscal_year_end;
"""


growth_data = pd.read_sql_query(
    growth_query,
    connection
)


print("\nYEAR-OVER-YEAR REVENUE GROWTH")
print(growth_data.to_string(index=False))


connection.close()