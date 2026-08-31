import requests
import pandas as pd


url = (
    "https://www.bankofcanada.ca/valet/"
    "observations/V39079/json"
)

params = {
    "start_date": "2020-01-01",
    "end_date": "2025-12-31"
}


response = requests.get(
    url,
    params=params,
    timeout=30
)

response.raise_for_status()

data = response.json()


rows = []

for item in data["observations"]:
    rows.append({
        "date": item["d"],
        "policy_rate": item["V39079"]["v"]
    })


policy_rate = pd.DataFrame(rows)

policy_rate["date"] = pd.to_datetime(
    policy_rate["date"]
)

policy_rate["policy_rate"] = pd.to_numeric(
    policy_rate["policy_rate"]
)


print("\nBANK OF CANADA POLICY RATE")
print(policy_rate.tail(20).to_string(index=False))


# Canadian Consumer Price Index
cpi_url = (
    "https://www.bankofcanada.ca/valet/"
    "observations/V41690973/json"
)

cpi_response = requests.get(
    cpi_url,
    params=params,
    timeout=30
)

cpi_response.raise_for_status()

cpi_data = cpi_response.json()


cpi_rows = []

for item in cpi_data["observations"]:
    cpi_rows.append({
        "date": item["d"],
        "cpi": item["V41690973"]["v"]
    })


cpi = pd.DataFrame(cpi_rows)

cpi["date"] = pd.to_datetime(cpi["date"])

cpi["cpi"] = pd.to_numeric(
    cpi["cpi"]
)


# Calculate year-over-year inflation
cpi["inflation_pct"] = (
    cpi["cpi"].pct_change(12) * 100
)


print("\nCANADIAN CPI AND INFLATION")
print(
    cpi.tail(20).to_string(
        index=False,
        formatters={
            "cpi": "{:.1f}".format,
            "inflation_pct": "{:.2f}".format
        }
    )
)




# Convert the daily policy rate to monthly observations
monthly_policy_rate = (
    policy_rate
    .set_index("date")
    .resample("MS")
    .last()
    .reset_index()
)


# Combine policy rate, CPI, and inflation
macro_data = cpi.merge(
    monthly_policy_rate,
    on="date",
    how="left"
)


# Keep the main analysis period
macro_data = macro_data[
    macro_data["date"].dt.year >= 2021
].copy()


print("\nCANADIAN MACRO DATA")

print(
    macro_data.tail(20).to_string(
        index=False,
        formatters={
            "cpi": "{:.1f}".format,
            "inflation_pct": "{:.2f}".format,
            "policy_rate": "{:.2f}".format
        }
    )
)


# Validate before saving
if macro_data[
    ["cpi", "inflation_pct", "policy_rate"]
].isna().any().any():
    raise ValueError(
        "Macro dataset still contains missing values."
    )


macro_data.to_csv(
    "data/processed/canadian_macro.csv",
    index=False
)


print("\nMacro data validation passed.")
print("Saved to data/processed/canadian_macro.csv")