"""
PACKAGES
"""
import csv
import json
import numpy as np
import datetime
import pandas as pd
import requests
from urllib.request import Request, urlopen
from email.message import EmailMessage
import ssl
import smtplib
from pretty_html_table import build_table


'''
API credentials
'''
apikey = 'NJ26SD97G2URK3V0'


'''
FUNCTIONS
'''
def earnings_extraction(date):
    CSV_URL = 'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&horizon=1month&apikey={}'.format(apikey)
    extr_list = []
    with requests.Session() as s:
        download = s.get(CSV_URL)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        for row in my_list:
            extr_list.append(row)
        df = pd.DataFrame.from_records(extr_list)
    df = df.drop(0, axis=0)
    df.columns = ['symbol', 'name', 'reportDate', 'fiscalDateEnding', 'estimate', 'currency']
    df['reportDate'] = df['reportDate'].map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
    today = date
    seven_days = date + datetime.timedelta(days=7)
    df = df[(df['reportDate'] >= today) & (df['reportDate'] <= seven_days) & (df['currency'] == 'USD')]
    return df


def past_earnings_extraction(dir):
    df = pd.read_csv(dir)
    df = df[['Symbol', 'Name', 'Report date', 'Est. earnings']]
    length, i = len(df.index), 0
    df['Reported EPS'], df['Surprise'], df['Surprise (%)'] = np.repeat(np.nan, 4), np.repeat(np.nan, 4), np.repeat(np.nan, 4)
    for (symbol, date) in zip(df['Symbol'], df['Report date']):
        url = 'https://www.alphavantage.co/query?function=EARNINGS&symbol={}&apikey={}'.format(symbol, apikey)
        r = requests.get(url)
        EPS = json.loads(json.dumps(r.json()))['quarterlyEarnings']
        last_EPS = [x for x in EPS if x['reportedDate'] == date]
        df.loc[i, 'Reported EPS'] = last_EPS[0]['reportedEPS']
        df.loc[i, 'Surprise'] = last_EPS[0]['surprise']
        df.loc[i, 'Surprise (%)'] = round(float(last_EPS[0]['surprisePercentage']), 2)
        i += 1
    df.to_csv(dir, index=False)
    return df


def main_indices():

    def setting_permissions(webpage):
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        request_site = Request(webpage, headers={"User-Agent": user_agent})
        web = urlopen(request_site).read()
        df = pd.read_html(web)[0]
        return df

    ## S&P500
    sp500 = setting_permissions('https://www.slickcharts.com/sp500')
    sp500_tickers = sorted(sp500['Symbol'].apply(lambda x: x.replace('.', '-')).tolist())

    ## DJIA30
    djia30 = setting_permissions('https://www.slickcharts.com/dowjones')
    djia_tickers = sorted(djia30['Symbol'].apply(lambda x: x.replace('.', '-')).tolist())

    ## NASDAQ100
    nasdaq100 = setting_permissions('https://www.slickcharts.com/nasdaq100')
    nasdaq_tickers = sorted(nasdaq100['Symbol'].apply(lambda x: x.replace('.', '-')).tolist())

    ### Concatenation
    concat = pd.concat([sp500, djia30, nasdaq100])[['Symbol', 'Company']].groupby('Symbol').first().reset_index()
    concat.rename(columns={'Symbol': 'symbol'}, inplace=True)
    return concat


def email(df, df_previous):
    user = 'mensajepython@gmail.com'
    gen_password = 'brbgbxkhdwyjmafe'
    recipients = ['ricardosans98@gmail.com']    # Add more elements with more e-mails
    subject = 'Weekly Earnings Report'
    df_html = build_table(df, 'grey_light')
    df_previous_html = build_table(df_previous, 'grey_light')
    body = '''
            <!DOCTYPE html>
            <html>
                <p><strong><span style="font-family: Georgia, serif; font-size: 22px;">Weekly Earnings Report</span></strong></p>
                <p><br></p>
                <p><span style="font-family: Georgia, serif;">Find attached top companies reporting earnings this week:</span></p>
                <p><span style="font-family: Georgia, serif;">{}</span></p>
                <p><span style="font-family: Georgia, serif;"><br></span></p>
                <p><span style="font-family: Georgia, serif;">Last week, companies reported the following earnings per share:</span></p>
                <p>{}</p>
            </html>
            '''.format(df_html, df_previous_html)
    em = EmailMessage()
    em['From'] = user
    em['To'] = recipients
    em['Subject'] = subject
    em.set_content(body, subtype = 'html')
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(user, gen_password)
        smtp.sendmail(user, recipients, em.as_string())


'''
EXECUTION
'''
if __name__ == '__main__':
    date = datetime.datetime.strptime('2022/09/05', '%Y/%m/%d')
    week_earnings = earnings_extraction(date)
    ind_tickers = main_indices()
    df_now = pd.merge(week_earnings, ind_tickers, on='symbol')[['symbol', 'name', 'reportDate', 'estimate']]
    df_now = df_now.rename(columns={'symbol': 'Symbol',
                                        'name': 'Name',
                                        'reportDate': 'Report date',
                                        'estimate': 'Est. earnings'}).head(10)
    df_now.to_csv('../data/earnings/{}.csv'.format(date.date()), index=False)
    prev_date = date - datetime.timedelta(days=7)
    df_past = past_earnings_extraction('../data/earnings/{}.csv'.format(prev_date.date()))
    email(df_now, df_past)