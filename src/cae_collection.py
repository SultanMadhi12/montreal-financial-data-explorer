import requests
import pandas as pd


# CAE's SEC identifier
cik = "CIK0001173382"

url = f"https://data.sec.gov/api/xbrl/companyfacts/{cik}.json"

headers = {
    "User-Agent": "Montreal Financial Data Explorer Sultan.Madhi@outlook.com"
}


response = requests.get(
    url,
    headers=headers,
    timeout=30
)

response.raise_for_status()

data = response.json()





# Financial metrics we want to collect
metrics = {
    "revenue": "Revenue",
    "operating_income": "ProfitLossFromOperatingActivities",
    "net_income": "ProfitLoss",
    "total_assets": "Assets",
    "total_liabilities": "Liabilities",
    "cash": "CashAndCashEquivalents",
    "operating_cash_flow": "CashFlowsFromUsedInOperatingActivities"
}



def extract_annual_metric(data, concept):
    """
    Extract annual CAD values for one CAE financial concept.
    """

    values = data["facts"]["ifrs-full"][concept]["units"]["CAD"]

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

    # Keep the most recently filed value for each fiscal year-end
    metric_df = metric_df.sort_values("filed")

    metric_df = metric_df.drop_duplicates(
        subset="date",
        keep="last"
    )

    metric_df = metric_df.sort_values("date")

    return metric_df




# Combine all metrics into one table
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


print("\nCAE 2021-2025 DATA")
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
    raise ValueError("CAE dataset still contains missing values.")


# Save the cleaned dataset

financial_data.to_csv(
    "data/processed/cae_financials.csv",
    index=False
)

print("\nCAE data validation passed.")
print("Saved to data/processed/cae_financials.csv")