import requests
import pandas as pd


# CN's SEC identifier
cik = "CIK0000016868"

url = f"https://data.sec.gov/api/xbrl/companyfacts/{cik}.json"

headers = {
    "User-Agent": "Montreal Financial Data Explorer Sultan.Madhi@outlook.com"
}


# Download CN's financial data from the SEC
response = requests.get(
    url,
    headers=headers,
    timeout=30
)

response.raise_for_status()

data = response.json()


# Financial metrics we want to collect
metrics = {
    "revenue": "RevenueFromContractWithCustomerExcludingAssessedTax",
    "operating_income": "OperatingIncomeLoss",
    "net_income": "NetIncomeLoss",
    "total_assets": "Assets",
    "total_liabilities": "Liabilities",
    "cash": "CashAndCashEquivalentsAtCarryingValue",
    "operating_cash_flow": "NetCashProvidedByUsedInOperatingActivities"
}


def extract_annual_metric(data, concept):
    """
    Extract annual CAD values for one SEC financial concept.
    """

    values = data["facts"]["us-gaap"][concept]["units"]["CAD"]

    rows = []

    for item in values:
        if item.get("fp") == "FY":
            rows.append({
                "date": item.get("end"),
                "value": item.get("val"),
                "filed": item.get("filed")
            })

    metric_df = pd.DataFrame(rows)

    if metric_df.empty:
        return metric_df

    metric_df["date"] = pd.to_datetime(metric_df["date"])
    metric_df["filed"] = pd.to_datetime(metric_df["filed"])

    # The SEC may repeat the same fiscal year in later filings.
    # Keep the most recently filed value for each year-end.
    metric_df = metric_df.sort_values("filed")

    metric_df = metric_df.drop_duplicates(
        subset="date",
        keep="last"
    )

    metric_df = metric_df.sort_values("date")

    return metric_df


# Start with an empty final table
financial_data = None


for metric_name, concept in metrics.items():

    metric_df = extract_annual_metric(
        data,
        concept
    )

    metric_df = metric_df[
        ["date", "value"]
    ]

    metric_df = metric_df.rename(
        columns={"value": metric_name}
    )

    if financial_data is None:
        financial_data = metric_df
    else:
        financial_data = financial_data.merge(
            metric_df,
            on="date",
            how="outer"
        )


financial_data = financial_data.sort_values("date")


financial_data = financial_data[
    financial_data["date"].dt.year >= 2021
].copy()




# Load values used to fill gaps in the SEC data
supplement = pd.read_csv(
    "data/raw/cn_annual_report_supplement.csv",
    parse_dates=["date"]
)


# Use SEC values first and annual-report values only where SEC data is missing
financial_data = (
    financial_data
    .set_index("date")
    .combine_first(supplement.set_index("date"))
    .reset_index()
    .sort_values("date")
)


print("\nCN COMPLETE 2021-2025 DATA")
print(financial_data.to_string(index=False))




# Final validation

expected_columns = [
    "date",
    "revenue",
    "operating_income",
    "net_income",
    "total_assets",
    "total_liabilities",
    "cash",
    "operating_cash_flow"
]

if financial_data[expected_columns].isna().any().any():
    raise ValueError("CN dataset still contains missing values.")


# Save the cleaned dataset

financial_data.to_csv(
    "data/processed/cn_financials.csv",
    index=False
)

print("\nCN data validation passed.")
print("Saved to data/processed/cn_financials.csv")