"""
PACKAGES
"""
import pandas as pd
import datetime
import json
import pandas
import requests
import http.client, urllib.parse
from bs4 import BeautifulSoup


'''
VARIABLES
'''
marketaux_api = 'KrIL4Vsk3gN0Urh321oUHk5WI0cjMbUNYKqBiMyv'
bloomberg_web = 'https://www.bloomberg.com/markets'

'''
CODE
'''
def extract_news(delay = 5):
    conn = http.client.HTTPSConnection('api.marketaux.com')
    after_this_time = (datetime.datetime.utcnow() - datetime.timedelta(minutes=delay)).strftime("%Y-%m-%dT%H:%M:%S")
    params = urllib.parse.urlencode({
        'api_token': marketaux_api,
        'exchanges': 'NYSE, NASDAQ, NYSEAMERICAN, BATS, NYSEARCA',
        'entity_types': 'equity',
        'countries': 'us',
        'languages': 'en,es',
        'published_before': after_this_time
        })

    conn.request('GET', '/v1/news/all?{}'.format(params))

    res = conn.getresponse()
    data = res.read().decode('utf-8')
    data = json.loads(data)
    return data


if __name__ == '__main__':
    '''data = extract_news(5)
    while True:
        try:
            for i in range(9999):
                print(data['data'][i]['entities'][0]['symbol'])
        except:
            break'''
    bloomberg()