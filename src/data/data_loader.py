"""
data_loader.py
--------------
This module provides functions to download raw financial data for a given ticker using yfinance.
The raw data is saved as CSV files in the data/raw/ directory for further processing.
"""

import os
import yfinance as yf
import pandas as pd

def create_directory_if_not_exists(path):
    """Ensure that the given directory exists."""
    if not os.path.exists(path):
        os.makedirs(path)

def download_financial_data(ticker_symbol, output_dir='data/raw'):
    """
    Download raw financial data for a ticker and save as CSV files.

    Parameters:
        ticker_symbol (str): The ticker symbol (e.g., 'AAPL').
        output_dir (str): Directory to save the raw data. Defaults to 'data/raw'.

    Returns:
        dict: A dictionary with DataFrames for 'financials', 'balance_sheet', and 'cashflow'.
    """
    # Create a yfinance Ticker object
    ticker = yf.Ticker(ticker_symbol)
    
    # Download the data
    financials = ticker.financials
    balance_sheet = ticker.balance_sheet
    cashflow = ticker.cashflow
    
    # Create the output directory if it doesn't exist
    create_directory_if_not_exists(output_dir)
    
    # Save the DataFrames to CSV files if they are not empty
    if not financials.empty:
        financials.to_csv(os.path.join(output_dir, f"{ticker_symbol}_financials.csv"))
    if not balance_sheet.empty:
        balance_sheet.to_csv(os.path.join(output_dir, f"{ticker_symbol}_balance_sheet.csv"))
    if not cashflow.empty:
        cashflow.to_csv(os.path.join(output_dir, f"{ticker_symbol}_cashflow.csv"))
    
    return {
        'financials': financials,
        'balance_sheet': balance_sheet,
        'cashflow': cashflow,
    }

if __name__ == "__main__":
    # If the script is run directly, use a default ticker or one provided as an argument.
    import sys
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
    else:
        symbol = "AAPL"  # default ticker

    data = download_financial_data(symbol)
    
    # Print summaries of the downloaded data for verification
    print(f"Downloaded data for {symbol}:")
    print("\nFinancials (Income Statement):")
    print(data['financials'].head())
    print("\nBalance Sheet:")
    print(data['balance_sheet'].head())
    print("\nCash Flow Statement:")
    print(data['cashflow'].head())