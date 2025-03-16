import streamlit as st
import pandas as pd
import yfinance as yf
import random  # used here only for demonstration purposes

# Dictionary mapping index names to their Wikipedia URLs
INDEXES = {
    "Dow Jones Industrial Average": "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average",
    "S&P 500": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
    "CAC 40": "https://en.wikipedia.org/wiki/CAC_40",
    "IBEX 35": "https://en.wikipedia.org/wiki/IBEX_35",
    "FTSE 100": "https://en.wikipedia.org/wiki/FTSE_100"
}

def get_tickers(index_name):
    """
    Extract tickers from the Wikipedia page corresponding to the selected index.
    
    For many indices (like DJIA and S&P 500), the table contains a "Symbol" column.
    You may need to adjust this for other indices if the table structure differs.
    """
    url = INDEXES[index_name]
    try:
        tables = pd.read_html(url)
    except Exception as e:
        st.error(f"Error reading tables from {url}: {e}")
        return []
    
    tickers = []
    # Try to locate a table with a "Symbol" column
    for table in tables:
        if "Symbol" in table.columns:
            tickers = table["Symbol"].tolist()
            break

    # Clean up tickers (optional): Remove any footnotes, spaces, etc.
    tickers = [str(t).split()[0] for t in tickers]
    return tickers

def compute_piotroski_score(ticker_symbol):
    """
    Compute the Piotroski F-Score for a ticker.
    
    In a full implementation, you would download financial statements,
    calculate each of the 9 components, and sum the binary results.
    
    For demonstration purposes, we return a random score.
    """
    # In a real-world case, use your financial data extraction and computations.
    return random.randint(0, 9)

# --- Streamlit GUI ---
st.title("Index Piotroski Score Dashboard")
st.write("Select an index below to extract tickers and view their Piotroski F-Scores.")

# Index selection
selected_index = st.selectbox("Select an index", list(INDEXES.keys()))

# Extract tickers from the chosen index
tickers = get_tickers(selected_index)

if tickers:
    st.write(f"Found {len(tickers)} tickers for {selected_index}.")
    
    # Compute a Piotroski F-Score for each ticker
    results = []
    for t in tickers:
        score = compute_piotroski_score(t)
        results.append({"Ticker": t, "Piotroski Score": score})
    
    # Convert results to a DataFrame and display it
    df_results = pd.DataFrame(results)
    st.dataframe(df_results)
else:
    st.error("No tickers found for the selected index.")