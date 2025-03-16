"""
data_loader.py
--------------
This file extracts ticker symbols from various Wikipedia pages (for different stock indexes),
downloads their financial statements (income statement, balance sheet, cash flow)
via yfinance, and saves them as CSV files in data/raw/.
"""

import os
import pandas as pd
import yfinance as yf

# Dictionary mapping index names to their Wikipedia URLs
INDEXES = {
    "Dow Jones Industrial Average": "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average",
    "S&P 500": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
    "CAC 40": "https://en.wikipedia.org/wiki/CAC_40",
    "IBEX 35": "https://en.wikipedia.org/wiki/IBEX_35",
    "FTSE 100": "https://en.wikipedia.org/wiki/FTSE_100"
}

def create_directory_if_not_exists(path: str) -> None:
    # This function creates the directory if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)

def get_tickers_from_wikipedia(index_name: str) -> list:
    # This function extracts a list of ticker symbols from their corresponding wikipedia page
    # The parameter __index_name__ is the name of the index (e.g. 'Dow Jones Industrial Average')
    url = INDEXES.get(index_name)
    if not url:
        print(f"Error: No URL found for index '{index_name}'. Check the INDEXES dictionary.")
        return []

    try:
        tables = pd.read_html(url)
    except Exception as excep:
        print(f"Error reading tables from {url}: {excep}")
        return []

    tickers = []
    # Look for a table with a 'Symbol' column
    for table in tables:
        if "Symbol" in table.columns:
            # Convert all values to string splitting on spaces to remove footnotes.
            tickers = [str(t).split()[0] for t in table["Symbol"].tolist()]
            break

    if not tickers:
        print(f"No tickers found on {url} with a 'Symbol' column.")
    else:
        print(f"Found {len(tickers)} tickers for {index_name}.")
    return tickers

def download_statements_for_ticker(ticker_symbol: str, output_dir: str) -> None:
    # This function downloads the financials, balance_sheet and cash_flow statement of the ticker_symbol passed as a parameter and save it as a CSV file.
    # Later we will use this function to get all financials, balance_sheet and cash_flow from each symbol of each index.

    ticker = yf.Ticker(ticker_symbol)

    financials = ticker.financials
    balance_sheet = ticker.balance_sheet
    cash_flow = ticker.cashflow

    # Save each DataFrame if it's not empty
    if not financials.empty:
        financials.to_csv(os.path.join(output_dir, f"{ticker_symbol}_financials.csv"))
    if not balance_sheet.empty:
        balance_sheet.to_csv(os.path.join(output_dir, f"{ticker_symbol}_balance_sheet.csv"))
    if not cash_flow.empty:
        cash_flow.to_csv(os.path.join(output_dir, f"{ticker_symbol}_cashflow.csv"))

def download_data_for_index(index_name: str, base_output_dir: str = "data/raw") -> None:
    # Using the get_tickers_from_wikipedia function previously defined, for a given index, the Wikipedia page 
    # is scraped to get its tickers. Then, it downloads each ticker's financial statements and saves them in data/raw/<index name>
    
    # Get the list of tickers from Wikipedia
    tickers = get_tickers_from_wikipedia(index_name)
    if not tickers:
        print(f"No tickers to download for {index_name}.")
        return

    # Create a subdirectory for this index
    index_output_dir = os.path.join(base_output_dir, index_name.replace(" ", "_"))
    create_directory_if_not_exists(index_output_dir)

    # Download statements for each ticker
    for symbol in tickers:
        try:
            download_statements_for_ticker(symbol, index_output_dir)
        except Exception as e:
            print(f"Error downloading data for {symbol}: {e}")

def download_all_indexes(base_output_dir: str = "data/raw") -> None:
    # This function downloads the financial data for all indexes declared in the INDEXES variable.

    for index_name in INDEXES.keys():
        print(f"\n--- Downloading data for {index_name} ---")
        download_data_for_index(index_name, base_output_dir)

if __name__ == "__main__":

    download_all_indexes()