import pandas as pd


def add_financial_metrics(df):
    """
    Add the main financial ratios used in the project.
    """

    result = df.copy()

    result = result.sort_values(
        ["company_name", "fiscal_year_end"]
    )


    # Revenue growth compared with the previous fiscal year
    result["revenue_growth_pct"] = (
        result
        .groupby("company_name")["revenue"]
        .pct_change(fill_method=None)
        * 100
    )


    # Avoid dividing by zero
    revenue = result["revenue"].replace(0, pd.NA)
    assets = result["total_assets"].replace(0, pd.NA)


    result["operating_margin_pct"] = (
        result["operating_income"] / revenue
        * 100
    )


    result["net_margin_pct"] = (
        result["net_income"] / revenue
        * 100
    )


    result["liabilities_to_assets_pct"] = (
        result["total_liabilities"] / assets
        * 100
    )


    result["operating_cash_flow_margin_pct"] = (
        result["operating_cash_flow"] / revenue
        * 100
    )


    return result