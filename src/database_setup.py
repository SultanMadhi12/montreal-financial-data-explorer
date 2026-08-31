import sqlite3
from pathlib import Path

import pandas as pd



# Project paths


project_root = Path(__file__).resolve().parents[1]

processed_dir = project_root / "data" / "processed"
database_path = project_root / "data" / "financial_data.db"



# Company information


companies = {
    "Lightspeed": {
        "ticker": "LSPD",
        "industry": "Technology",
        "currency": "USD",
        "file": "lightspeed_financials.csv"
    },

    "Canadian National Railway": {
        "ticker": "CNR",
        "industry": "Rail Transportation",
        "currency": "CAD",
        "file": "cn_financials.csv"
    },

    "CAE": {
        "ticker": "CAE",
        "industry": "Aerospace",
        "currency": "CAD",
        "file": "cae_financials.csv"
    }
}



# Connect to SQLite


connection = sqlite3.connect(database_path)

cursor = connection.cursor()

# Make sure SQLite enforces relationships between tables
cursor.execute("PRAGMA foreign_keys = ON;")



# Rebuild the database tables


# This lets us run the setup script again without
# creating duplicate rows.
cursor.execute("DROP TABLE IF EXISTS financials;")
cursor.execute("DROP TABLE IF EXISTS companies;")
cursor.execute("DROP TABLE IF EXISTS macro_data;")



# Companies table


cursor.execute("""
CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY,
    company_name TEXT NOT NULL,
    ticker TEXT NOT NULL UNIQUE,
    industry TEXT NOT NULL,
    currency TEXT NOT NULL
);
""")



# Financial data table


cursor.execute("""
CREATE TABLE financials (
    financial_id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL,
    fiscal_year_end TEXT NOT NULL,
    revenue REAL,
    operating_income REAL,
    net_income REAL,
    total_assets REAL,
    total_liabilities REAL,
    cash REAL,
    operating_cash_flow REAL,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id),

    UNIQUE (company_id, fiscal_year_end)
);
""")



# Canadian macroeconomic data table


cursor.execute("""
CREATE TABLE macro_data (
    macro_id INTEGER PRIMARY KEY,
    date TEXT NOT NULL UNIQUE,
    cpi REAL NOT NULL,
    inflation_pct REAL NOT NULL,
    policy_rate REAL NOT NULL
);
""")



# Load company financial data


for company_name, company_info in companies.items():

    # Add the company to the companies table
    cursor.execute(
        """
        INSERT INTO companies (
            company_name,
            ticker,
            industry,
            currency
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            company_name,
            company_info["ticker"],
            company_info["industry"],
            company_info["currency"]
        )
    )

    # SQLite gives us the ID of the company we just inserted
    company_id = cursor.lastrowid


    # Load that company's processed CSV
    file_path = processed_dir / company_info["file"]

    df = pd.read_csv(file_path)

    df["date"] = pd.to_datetime(df["date"])


    # Add each fiscal year to the financials table
    for row in df.itertuples(index=False):

        cursor.execute(
            """
            INSERT INTO financials (
                company_id,
                fiscal_year_end,
                revenue,
                operating_income,
                net_income,
                total_assets,
                total_liabilities,
                cash,
                operating_cash_flow
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company_id,
                row.date.strftime("%Y-%m-%d"),
                float(row.revenue),
                float(row.operating_income),
                float(row.net_income),
                float(row.total_assets),
                float(row.total_liabilities),
                float(row.cash),
                float(row.operating_cash_flow)
            )
        )



# Load Canadian macroeconomic data


macro_path = processed_dir / "canadian_macro.csv"

macro_df = pd.read_csv(macro_path)

macro_df["date"] = pd.to_datetime(
    macro_df["date"]
)


for row in macro_df.itertuples(index=False):

    cursor.execute(
        """
        INSERT INTO macro_data (
            date,
            cpi,
            inflation_pct,
            policy_rate
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            row.date.strftime("%Y-%m-%d"),
            float(row.cpi),
            float(row.inflation_pct),
            float(row.policy_rate)
        )
    )



# Save database changes


connection.commit()



# Quick validation


company_count = cursor.execute(
    "SELECT COUNT(*) FROM companies"
).fetchone()[0]


financial_count = cursor.execute(
    "SELECT COUNT(*) FROM financials"
).fetchone()[0]


macro_count = cursor.execute(
    "SELECT COUNT(*) FROM macro_data"
).fetchone()[0]


print(f"\nCompanies loaded: {company_count}")
print(f"Financial rows loaded: {financial_count}")
print(f"Macro rows loaded: {macro_count}")
print(f"Database created: {database_path}")


connection.close()