"""
PACKAGES
"""
import csv
import time
import random
import datetime
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

'''
VARIABLES
'''
web = 'https://stockanalysis.com/stocks/'
alpha_key = 'Insert API Key'

'''
FUNCTIONS
'''


def extraction(webpage):
    dictionary = dict(symbol=list(),
                      company=list(),
                      industry=list(),
                      market_cap=list())
    driver = webdriver.Chrome()
    driver.get(webpage)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    while True:
        driver.implicitly_wait(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find("tbody")
        rows = table.find_all('tr')
        for tr in rows:
            td = tr.find_all('td')
            row = [tr.text for tr in td]
            dictionary['symbol'].append(row[0])
            dictionary['company'].append(row[1])
            dictionary['industry'].append(row[2])
            dictionary['market_cap'].append(row[3])
        driver.find_element(By.XPATH, "//*[contains(text(), 'Next')]").click()
        time.sleep(1)

    table = pd.DataFrame(dictionary)

    df.to_csv('../data/stockanalysis.csv', index=False)
    driver.quit()


def correction():
    companies = pd.read_csv('../data/stockanalysis.csv', sep=",")
    industries = pd.read_csv('../data/industries.csv', sep=";")
    df_merge = pd.merge(companies, industries, on='industry', how='left')[
        ['symbol', 'company', 'correct_industry', 'sector', 'market_cap']]
    df_merge.rename(columns={'correct_industry': 'industry'}, inplace=True)
    df_merge.to_csv('../data/stockanalysis.csv', index=False)


def alpha_stocks(day):
    CSV_URL = 'https://www.alphavantage.co/query?function=LISTING_STATUS&date={}&state=active&apikey={}'.format(day,
                                                                                                                alpha_key)
    with requests.Session() as s:
        download = s.get(CSV_URL)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        with open('../data/alpha_stocks.csv', 'a', newline='') as csvfile:
            to_csv = csv.writer(csvfile, delimiter=',')
            # next(cr)
            for row in cr:
                to_csv.writerow(row)
        df = pd.read_csv('../data/alpha_stocks.csv')
        df.columns = ['symbol', 'name', 'exchange', 'assetType', 'ipoDate', 'delistingDate', 'status']
        df = df[df['assetType'] == 'Stock']
        df.to_csv('../data/alpha_stocks.csv', index=False)


def table_unions():
    stockanalysis = pd.read_csv('../data/stockanalysis.csv')
    alpha = pd.read_csv('../data/alpha_stocks.csv')
    df_merge = pd.merge(stockanalysis, alpha, on='symbol', how='outer').drop_duplicates()
    df_merge['company_name'] = df_merge.name.combine_first(df_merge.company)  # Coalesce
    df_merge = df_merge[['symbol', 'company_name', 'exchange', 'ipoDate', 'industry', 'sector', 'market_cap']]
    df_merge.to_csv('../data/stocks.csv', index=False)


'''
EXECUTION
'''
if __name__ == '__main__':
    extraction(web)
    correction()
    alpha_stocks(datetime.date.today())
    table_unions()
