"""
PACKAGES
"""
import tecanal
import requests
import pandas as pd


def main():
    """
    VARIABLES
    """
    api_key = 'Insert API key'

    """
    CODE
    """
    symbol = 'AAPL'
    params_SMA = {
        'symbols': symbol,
        'intervals': ['1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'],
        'time_periods': [5, 10, 20, 50, 100, 200]
    }
    SMA_func(params_SMA, api_key)


def SMA_func(param_grid, key):
    for symbol in param_grid['symbols']:
        for interval in param_grid['intervals']:
            for time_period in param_grid['time_periods']:
                url = 'https://www.alphavantage.co/query?function=SMA&symbol=' + symbol + '&interval=' + \
                      interval + '&time_period=' + str(time_period) + '&series_type=close&apikey=' + key
                r = requests.get(url)
                data = r.json()

                print(data)




if __name__ == '__main__':
    main()
