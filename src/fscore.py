"""
fscore.py
---------

This module provides functions to compute the Piotroski F-Score for a given ticker.
It uses financial statement data from:
  - Income Statement (financials)
  - Balance Sheet (balance_sheet)
  - Cash Flow Statement (cash_flow)
  
Assumptions:
  - The DataFrames contain at least two columns: the current period and the previous period.
  - Row labels must match those provided by yfinance (e.g., "Net Income", "Total Assets", etc.).
  - If any data is missing, the code either assumes a value of 0 or handles the error gracefully.
  - Each criterion function accepts the appropriate DataFrames along with two period keys:
    - curr: the current period
    - prev: the previous period

If the financial statements are not aligned (i.e. they do not share common periods),
the master function will only perform comparisons on the intersection of periods.

The 9 criteria (each scored as 1 if favorable, 0 otherwise) are:
  1. ROA Positive: Net Income / Total Assets > 0.
  2. OCF Positive: Operating Cash Flow > 0.
  3. ROA Improvement: Current ROA > Previous ROA.
  4. Quality of Earnings: Operating Cash Flow > Net Income.
  5. Leverage Improvement: Current leverage (Long Term Debt / Total Assets) is lower than previous.
  6. Liquidity Improvement: Current ratio (Current Assets / Current Liabilities) is higher than previous.
  7. No Dilution: Shares Outstanding did not increase.
  8. Gross Margin Improvement: Current gross margin > Previous gross margin.
  9. Asset Turnover Improvement: Current asset turnover > Previous asset turnover.
  
The final Piotroski F-Score is the sum of these 9 binary criteria.
"""

def get_common_periods(financials, balance_sheet, cash_flow):
    # This function returns a sorted (descending) list of common periods (column names) across all statements.
    periods_fin = set(financials.columns)
    periods_bs = set(balance_sheet.columns)
    periods_cf = set(cash_flow.columns)
    common = periods_fin & periods_bs & periods_cf
    # Sort descending (assuming period names can be sorted as strings or timestamps)
    common_sorted = sorted(common, reverse=True)
    return common_sorted

def criterion_1(financials, balance_sheet, curr, prev):
    # Criterion 1: ROA Positive.
    # If (Net Income / Total Assets) in the current period > 0, return 1,  else 0.
    try:
        net_income = financials.loc["Net Income", curr]
        total_assets = balance_sheet.loc["Total Assets", curr]
    except KeyError:
        return 0
    roa = net_income / total_assets if total_assets else 0
    return 1 if roa > 0 else 0

def criterion_2(cash_flow, curr):
    # Criterion 2: Operating Cash Flow Positive.
    # If Operating Cash Flow (Total Cash From Operating Activities) in current period > 0, return 1, else 0.
    try:
        ocf = cash_flow.loc["Total Cash From Operating Activities", curr]
    except KeyError:
        return 0
    return 1 if ocf > 0 else 0

def criterion_3(financials, balance_sheet, curr, prev):
    # Criterion 3: ROA Improvement.
    # If current period ROA > previous period ROA, return 1, else 0.
    try:
        net_income_curr = financials.loc["Net Income", curr]
        total_assets_curr = balance_sheet.loc["Total Assets", curr]
        net_income_prev = financials.loc["Net Income", prev]
        total_assets_prev = balance_sheet.loc["Total Assets", prev]
    except KeyError:
        return 0
    roa_curr = net_income_curr / total_assets_curr if total_assets_curr else 0
    roa_prev = net_income_prev / total_assets_prev if total_assets_prev else 0
    return 1 if roa_curr > roa_prev else 0

def criterion_4(financials, cash_flow, curr):
    # Criterion 4: Quality of Earnings.
    # If Operating Cash Flow in current period > Net Income in current period, return 1, else 0.
    try:
        net_income = financials.loc["Net Income", curr]
        ocf = cash_flow.loc["Total Cash From Operating Activities", curr]
    except KeyError:
        return 0
    return 1 if ocf > net_income else 0

def criterion_5(balance_sheet, curr, prev):
    # Criterion 5: Leverage Improvement.
    # If (Long Term Debt / Total Assets) in current period is less than in previous period, return 1, else 0.
    try:
        ltd_curr = balance_sheet.loc["Long Term Debt", curr]
        total_assets_curr = balance_sheet.loc["Total Assets", curr]
        ltd_prev = balance_sheet.loc["Long Term Debt", prev]
        total_assets_prev = balance_sheet.loc["Total Assets", prev]
    except KeyError:
        return 0
    leverage_curr = ltd_curr / total_assets_curr if total_assets_curr else 0
    leverage_prev = ltd_prev / total_assets_prev if total_assets_prev else 0
    return 1 if leverage_curr < leverage_prev else 0

def criterion_6(balance_sheet, curr, prev):
    # Criterion 6: Liquidity Improvement.
    # If current ratio (Total Current Assets / Total Current Liabilities) in current period is higher than in previous period, return 1, else 0.
    try:
        ca_curr = balance_sheet.loc["Total Current Assets", curr]
        cl_curr = balance_sheet.loc["Total Current Liabilities", curr]
        ca_prev = balance_sheet.loc["Total Current Assets", prev]
        cl_prev = balance_sheet.loc["Total Current Liabilities", prev]
    except KeyError:
        return 0
    ratio_curr = ca_curr / cl_curr if cl_curr else 0
    ratio_prev = ca_prev / cl_prev if cl_prev else 0
    return 1 if ratio_curr > ratio_prev else 0

def criterion_7(balance_sheet, curr, prev):
    # Criterion 7: No Dilution.
    # If Shares Outstanding in current period is less than or equal to that in previous period, return 1, else 0.
    try:
        shares_curr = balance_sheet.loc["Shares Outstanding", curr]
        shares_prev = balance_sheet.loc["Shares Outstanding", prev]
    except KeyError:
        return 1  # Assume no dilution if data is missing
    return 1 if shares_curr <= shares_prev else 0

def criterion_8(financials, curr, prev):
    # Criterion 8: Gross Margin Improvement, where Gross Margin = (Total Revenue - Cost Of Revenue) / Total Revenue.
    # If Gross Margin in current period is higher than in previous period, return 1, else 0.
    try:
        revenue_curr = financials.loc["Total Revenue", curr]
        cogs_curr = financials.loc["Cost Of Revenue", curr]
        revenue_prev = financials.loc["Total Revenue", prev]
        cogs_prev = financials.loc["Cost Of Revenue", prev]
    except KeyError:
        return 0
    gm_curr = (revenue_curr - cogs_curr) / revenue_curr if revenue_curr else 0
    gm_prev = (revenue_prev - cogs_prev) / revenue_prev if revenue_prev else 0
    return 1 if gm_curr > gm_prev else 0

def criterion_9(financials, balance_sheet, curr, prev):
    # Criterion 9: Asset Turnover Improvement.
    # If Asset Turnover (Total Revenue / Total Assets) in current period is higher than in previous period, return 1, else 0.
    try:
        revenue_curr = financials.loc["Total Revenue", curr]
        revenue_prev = financials.loc["Total Revenue", prev]
        total_assets_curr = balance_sheet.loc["Total Assets", curr]
        total_assets_prev = balance_sheet.loc["Total Assets", prev]
    except KeyError:
        return 0
    turnover_curr = revenue_curr / total_assets_curr if total_assets_curr else 0
    turnover_prev = revenue_prev / total_assets_prev if total_assets_prev else 0
    return 1 if turnover_curr > turnover_prev else 0

def compute_piotroski_fscore(financials, balance_sheet, cash_flow):
    """
    Master function that computes the Piotroski F-Score.
    It first identifies the common reporting periods across all three statements,
    then computes the score based on the two most recent common periods.
    
    Returns:
      A dictionary with:
         - "Period": (current_period, previous_period)
         - Each criterion score (criterion_1 to criterion_9)
         - "Total_FScore": sum of criteria scores.
    """
    common_periods = get_common_periods(financials, balance_sheet, cash_flow)
    if len(common_periods) < 2:
        raise ValueError("Not enough common reporting periods across the financial statements.")

    # Use the two most recent common periods
    curr, prev = common_periods[0], common_periods[1]

    scores = {}
    scores["criterion_1"] = criterion_1(financials, balance_sheet, curr, prev)
    scores["criterion_2"] = criterion_2(cash_flow, curr)
    scores["criterion_3"] = criterion_3(financials, balance_sheet, curr, prev)
    scores["criterion_4"] = criterion_4(financials, cash_flow, curr)
    scores["criterion_5"] = criterion_5(balance_sheet, curr, prev)
    scores["criterion_6"] = criterion_6(balance_sheet, curr, prev)
    scores["criterion_7"] = criterion_7(balance_sheet, curr, prev)
    scores["criterion_8"] = criterion_8(financials, curr, prev)
    scores["criterion_9"] = criterion_9(financials, balance_sheet, curr, prev)
    
    total = sum(scores.values())
    scores["Total_FScore"] = total
    scores["Period"] = (curr, prev)
    return scores

if __name__ == "__main__":
    # Demonstration with sample data
    import pandas as pd
    
    # Define two periods (e.g., as strings or timestamps)
    periods = ["2023-12-31", "2022-12-31"]
    
    # Sample Income Statement DataFrame
    financials_data = {
        "Net Income": [100, 80],
        "Total Revenue": [1000, 900],
        "Cost Of Revenue": [600, 550],
    }
    financials = pd.DataFrame(financials_data, index=periods).T
    
    # Sample Balance Sheet DataFrame
    balance_sheet_data = {
        "Total Assets": [5000, 4800],
        "Long Term Debt": [1000, 1100],
        "Total Current Assets": [1500, 1400],
        "Total Current Liabilities": [800, 850],
        "Shares Outstanding": [200, 210],
    }
    balance_sheet = pd.DataFrame(balance_sheet_data, index=periods).T
    
    # Sample Cash Flow DataFrame
    cash_flow_data = {
        "Total Cash From Operating Activities": [120, 100],
    }
    cash_flow = pd.DataFrame(cash_flow_data, index=periods).T

    # Compute and display the Piotroski F-Score breakdown for the two most recent common periods
    fscore_results = compute_piotroski_fscore(financials, balance_sheet, cash_flow)
    
    print("Piotroski F-Score Breakdown for periods", fscore_results["Period"], ":")
    for key, value in fscore_results.items():
        if key != "Period":
            print(f"{key}: {value}")