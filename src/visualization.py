import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from metrics import add_financial_metrics


# Project paths

project_root = Path(__file__).resolve().parents[1]

database_path = project_root / "data" / "financial_data.db"

charts_dir = project_root / "outputs" / "charts"

charts_dir.mkdir(
    parents=True,
    exist_ok=True
)


# Load financial data from SQLite

connection = sqlite3.connect(database_path)


financial_query = """
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
    financial_query,
    connection
)


macro_data = pd.read_sql_query(
    """
    SELECT
        date,
        cpi,
        inflation_pct,
        policy_rate
    FROM macro_data
    ORDER BY date;
    """,
    connection
)


connection.close()


# Prepare data

financial_data["fiscal_year_end"] = pd.to_datetime(
    financial_data["fiscal_year_end"]
)

financial_data["fiscal_year"] = (
    financial_data["fiscal_year_end"].dt.year
)


years = sorted(
    financial_data["fiscal_year"].unique()
)


macro_data["date"] = pd.to_datetime(
    macro_data["date"]
)


# Add the financial ratios created in metrics.py

financial_data = add_financial_metrics(
    financial_data
)


# 1. Indexed revenue growth

financial_data["revenue_index"] = (
    financial_data.groupby("company_name")["revenue"]
    .transform(lambda values: values / values.iloc[0] * 100)
)


fig, ax = plt.subplots(figsize=(10, 5))


for company, company_data in financial_data.groupby(
    "company_name"
):
    ax.plot(
        company_data["fiscal_year"],
        company_data["revenue_index"],
        marker="o",
        label=company
    )


ax.axhline(
    100,
    linewidth=1,
    linestyle="--"
)

ax.set_title("Indexed Revenue Growth (Base Year = 100)")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("Revenue Index")
ax.set_xticks(years)
ax.legend()

plt.tight_layout()

plt.savefig(
    charts_dir / "01_indexed_revenue_growth.png",
    dpi=200
)

plt.close()


# 2. Revenue growth

fig, ax = plt.subplots(figsize=(10, 5))


for company, company_data in financial_data.groupby(
    "company_name"
):
    ax.plot(
        company_data["fiscal_year"],
        company_data["revenue_growth_pct"],
        marker="o",
        label=company
    )


ax.axhline(0, linewidth=1)

ax.set_title("Year-over-Year Revenue Growth")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("Revenue Growth (%)")
ax.set_xticks(years)
ax.legend()

plt.tight_layout()

plt.savefig(
    charts_dir / "02_revenue_growth.png",
    dpi=200
)

plt.close()


# 3. Operating margin

fig, ax = plt.subplots(figsize=(10, 5))


for company, company_data in financial_data.groupby(
    "company_name"
):
    ax.plot(
        company_data["fiscal_year"],
        company_data["operating_margin_pct"],
        marker="o",
        label=company
    )


ax.axhline(0, linewidth=1)

ax.set_title("Operating Margin")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("Operating Margin (%)")
ax.set_xticks(years)
ax.legend()

plt.tight_layout()

plt.savefig(
    charts_dir / "03_operating_margin.png",
    dpi=200
)

plt.close()


# 4. Net profit margin

fig, ax = plt.subplots(figsize=(10, 5))


for company, company_data in financial_data.groupby(
    "company_name"
):
    ax.plot(
        company_data["fiscal_year"],
        company_data["net_margin_pct"],
        marker="o",
        label=company
    )


ax.axhline(0, linewidth=1)

ax.set_title("Net Profit Margin")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("Net Margin (%)")
ax.set_xticks(years)
ax.legend()

plt.tight_layout()

plt.savefig(
    charts_dir / "04_net_margin.png",
    dpi=200
)

plt.close()


# 5. Liabilities to assets

fig, ax = plt.subplots(figsize=(10, 5))


for company, company_data in financial_data.groupby(
    "company_name"
):
    ax.plot(
        company_data["fiscal_year"],
        company_data["liabilities_to_assets_pct"],
        marker="o",
        label=company
    )


ax.set_title("Liabilities as a Percentage of Total Assets")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("Liabilities / Assets (%)")
ax.set_xticks(years)
ax.legend()

plt.tight_layout()

plt.savefig(
    charts_dir / "05_liabilities_to_assets.png",
    dpi=200
)

plt.close()


# 6. Operating cash-flow margin

fig, ax = plt.subplots(figsize=(10, 5))


for company, company_data in financial_data.groupby(
    "company_name"
):
    ax.plot(
        company_data["fiscal_year"],
        company_data["operating_cash_flow_margin_pct"],
        marker="o",
        label=company
    )


ax.axhline(0, linewidth=1)

ax.set_title("Operating Cash-Flow Margin")
ax.set_xlabel("Fiscal Year")
ax.set_ylabel("Operating Cash-Flow Margin (%)")
ax.set_xticks(years)
ax.legend()

plt.tight_layout()

plt.savefig(
    charts_dir / "06_operating_cash_flow_margin.png",
    dpi=200
)

plt.close()


# 7. Canadian macroeconomic environment

fig, ax = plt.subplots(figsize=(10, 5))


ax.plot(
    macro_data["date"],
    macro_data["inflation_pct"],
    label="Inflation"
)

ax.plot(
    macro_data["date"],
    macro_data["policy_rate"],
    label="Bank of Canada Policy Rate"
)


ax.set_title("Canadian Inflation and Policy Interest Rate")
ax.set_xlabel("Date")
ax.set_ylabel("Percent (%)")
ax.legend()

plt.tight_layout()

plt.savefig(
    charts_dir / "07_canadian_macro_environment.png",
    dpi=200
)

plt.close()


print("\nCharts created successfully.")
print(f"Saved to: {charts_dir}")