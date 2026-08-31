import pandas as pd

df = pd.read_csv("lightspeed_financials.csv")

print("DATA VALIDATION")
print("----------------")

print("Missing values:")
print(df.isnull().sum())

print("\nData types:")
print(df.dtypes)

print("\nRevenue trend:")
print(df[["date", "revenue"]])

print("\nNet income trend:")
print(df[["date", "net_income"]])

print("\nValidation complete")