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

    import os
    import glob
    import pandas as pd
    from fscore import compute_piotroski_fscore

    # Mapping dictionaries for row renaming:
    INCOME_STATEMENT_ROW_MAP = {
        "Net Income": "Net Income",
        "Total Revenue": "Total Revenue",
        "Cost Of Revenue": "Cost Of Revenue"
        # Add more if needed
    }

    BALANCE_SHEET_ROW_MAP = {
        "Total Assets": "Total Assets",
        "Long Term Debt": "Long Term Debt",
        "Total Current Assets": "Total Current Assets",
        "Total Current Liabilities": "Total Current Liabilities",
        "Shares Outstanding": "Shares Outstanding"
        # Add more if needed
    }

    CASH_FLOW_ROW_MAP = {
        "Total Cash From Operating Activities": "Total Cash From Operating Activities"
        # Add more if needed
    }

    # Define the index folder (e.g., DJIA)
    index_folder = "Dow_Jones_Industrial_Average"
    base_dir = os.path.join("data", "raw", index_folder)

    # Use glob to find all income statement CSV files and extract tickers
    income_files = glob.glob(os.path.join(base_dir, "*_income_statement.csv"))
    tickers = [os.path.basename(f).split("_")[0] for f in income_files]

    results = []

    for ticker in tickers:
        print(f"\nProcessing ticker: {ticker}")
        
        # Construct file paths for income statement, balance sheet, and cash flow
        inc_file = os.path.join(base_dir, f"{ticker}_income_statement.csv")
        bs_file = os.path.join(base_dir, f"{ticker}_balance_sheet.csv")
        cf_file = os.path.join(base_dir, f"{ticker}_cashflow.csv")
        
        # Check if all required files exist
        if not (os.path.exists(inc_file) and os.path.exists(bs_file) and os.path.exists(cf_file)):
            print(f"  -> Missing one or more files for {ticker}. Skipping.")
            continue

        # Load CSV files into DataFrames (using the first column as index)
        income_statement = pd.read_csv(inc_file, index_col=0)
        balance_sheet = pd.read_csv(bs_file, index_col=0)
        cash_flow = pd.read_csv(cf_file, index_col=0)
        
        # Rename rows to standard labels
        income_statement.rename(index=INCOME_STATEMENT_ROW_MAP, inplace=True)
        balance_sheet.rename(index=BALANCE_SHEET_ROW_MAP, inplace=True)
        cash_flow.rename(index=CASH_FLOW_ROW_MAP, inplace=True)
        
        # Debug: print columns and row labels
        print("  Income Statement columns:", list(income_statement.columns))
        print("  Balance Sheet columns:", list(balance_sheet.columns))
        print("  Cash Flow columns:", list(cash_flow.columns))
        
        # Determine common reporting periods across the three statements
        common_periods = set(income_statement.columns) & set(balance_sheet.columns) & set(cash_flow.columns)
        if len(common_periods) < 2:
            print(f"  -> {ticker} does not have at least two common periods. Skipping.")
            continue
        else:
            common_sorted = sorted(common_periods, reverse=True)
            print("  -> Common periods:", common_sorted)
        
        # Compute the Piotroski F-Score for the ticker
        try:
            fscore_data = compute_piotroski_fscore(income_statement, balance_sheet, cash_flow)
            results.append({
                "Ticker": ticker,
                "FScore": fscore_data["Total_FScore"],
                "Current_Period": fscore_data["Period"][0],
                "Previous_Period": fscore_data["Period"][1],
                "Breakdown": fscore_data
            })
            print(f"  -> F-Score computed: {fscore_data['Total_FScore']}")
        except Exception as e:
            print(f"  -> Error computing F-Score for {ticker}: {e}")

    # Summarize the results in a DataFrame
    df_results = pd.DataFrame(results)

    print("\nPiotroski F-Scores for all tickers:")
    if not df_results.empty:
        # Sort alphabetically by Ticker
        df_results.sort_values(by="Ticker", inplace=True)
        print(df_results[["Ticker", "FScore", "Current_Period", "Previous_Period"]])
    else:
        print("No scores computed.")