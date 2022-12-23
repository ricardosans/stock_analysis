# stock_analysis
Repository containing various scripts on quant stock analysis and sentiment analysis for finance news.

- earning_emails.py: This code is meant to be run each Monday to get the estimated EPS of the firms disclosing earnings that week. It also provides an 
                     estimate vs. real EPS for those companies who reported earnings the previous week.
                     
- industries.py: This script automatically exctracts the name of those actively-tradad companies in the US and assigns an industry to them (e.g.,
                 Sanofi --> Pharmaceutical) by web scraping publicly available data on the internet.

- news.py: [Work in progress] This code pursues to extract text news from the Bloomberg.com webpage by means of webscraping.

- technical_analysis.py: [Work in progress] This script is meant to extract technical information from stock prices, such as the Simple Moving Average,
                         Bollinger Bands and others.
                         
Sources of information: www.alphavantage.co, www.bloomberg.com, www.stockanalysis.com
