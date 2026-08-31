import sqlite3
from pathlib import Path

import pandas as pd

from metrics import add_financial_metrics


project_root = Path(__file__).resolve().parents[1]

database_path = project_root / "data" / "financial_data.db"


connection = sqlite3.connect(database_path)


query = """
SELECT
    c.company_name,
    c.ticker,
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

connection.close()


financial_data = add_financial_metrics(
    financial_data
)


columns_to_show = [
    "company_name",
    "fiscal_year_end",
    "revenue_growth_pct",
    "operating_margin_pct",
    "net_margin_pct",
    "liabilities_to_assets_pct",
    "operating_cash_flow_margin_pct"
]


print("\nPYTHON FINANCIAL METRICS")

print(
    financial_data[columns_to_show]
    .round(2)
    .to_string(index=False)
)