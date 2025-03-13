# Data Science Project: Value Stock Selection with Piotroski F-Score

## Description

The goal of this project is to use the Piotroski F-Score to identify value stocks in the SP500, extracting data from Yahoo Finance. 

### Piotroski F-score
The Piotroski F-score is a rating system that goes from 0 to 9 that evaluates a company's financial strength where 9 is being the best. The score can be used to identify high-value stock for investment purposes. 
Please note that the contents of this project are for informational purposes only and should not be considered financial advice. Always consult with a professional financial advisor before making investment decisions.

The score is calculated based on 9 criteria divided into 3 groups.

#### Profitability

- Return on Assets (ROA) (1 point if it is positive in the current year, 0 otherwise);
- Operating Cash Flow (1 point if it is positive in the current year, 0 otherwise);
- Change in Return of Assets (ROA) (1 point if ROA is higher in the current year compared to the previous one, 0 otherwise);
- Accruals (1 point if Operating Cash Flow/Total Assets is higher than ROA/Total Assets in the current year, 0 otherwise);

#### Leverage, Liquidity and Source of Funds

- Change in Leverage (long-term) ratio (1 point if the ratio is lower this year compared to the previous one, 0 otherwise);
- Change in Current ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise);
- Change in the number of shares (1 point if no new shares were issued during the last year);

#### Operating Efficiency

- Change in Gross Margin (1 point if it is higher in the current year compared to the previous one, 0 otherwise);
- Change in Asset Turnover ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise);

More information can be read here: https://en.wikipedia.org/wiki/Piotroski_F-score

---

The project will cover the full cycle of a data science project, starting from data collection and manipulation to analysis, modeling and visualization of results.

## Features

- **Data Extraction:** Use of the Yahoo Finance API to download financial data.
- **Indicator Calculation:** Implement the Piotroski F-Score along with other financial indicators.
- **Comparative Analysis:** Compare the F-Score with additional key ratios.
- **Predictive Modeling:** Use machine learning techniques to forecast stock performance.
- **Backtesting:** Develop modules to simulate investment strategies based on the calculated indicators.
- **Visualization:** Create interactive dashboards and explanatory charts.
- **Documentation:** Organized code, detailed notebooks, and comprehensive project documentation.

## Requirements

- **Python:** Version 3.7 or higher.
- **Libraries:** pandas, numpy, matplotlib, scikit-learn, yfinance, among others (see `requirements.txt`).
- **Git:** For version control.

## Notes

Note: The setup.py file is provided for development purposes. 
End users can simply review the notebooks or interact with the deployed web application without installing the package.

