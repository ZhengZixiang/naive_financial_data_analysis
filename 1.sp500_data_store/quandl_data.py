# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
from urllib.request import urlopen


def construct_futures_symbols(symbol, start_year=2015, end_year=2017):
    """
    Constructs a list of futures contract codes for a particular symbol and timeframe.
    """
    futures = []
    # March, June, September and December delivery codes
    months = 'HMUZ'
    for y in range(start_year, end_year+1):
        for m in months:
            futures.append('%s%s%s' % (symbol, m, y))
    return futures


def download_contract_from_quandl(contract, dl_dir):
    """
    Download an individual futures contract from Quandl and  the store it to disk
    in the 'dl_dir' directory. An auth_token is required, which is obtained
    from the Quandl upon sign-up
    """
    # Construct the API call from the contract and auth_token
    api_call = 'https://www.quandl.com/api/v3/datasets/'
    api_call += 'CME/%s.csv' % contract
    # If you wish to add an auth token for more downloads, simply comment the following
    # line and replace MY_AUTH_TOKEN with your auth token in the line below
    params = '?sort_order=asc'
    # params = '?auto_token=MY_AUTH_TOKEN&sort_order=asc'
    full_url = '%s%s' % (api_call, params)
    print(full_url)
    # Download the data from Quandl
    data = urlopen(full_url).read().decode('utf-8')

    # Store the data to disk
    fc = open('%s/%s.csv' % (dl_dir, contract), 'w')
    fc.write(data)
    fc.close()


def download_historical_contracts(symbol, dl_dir, start_year=2015, end_year=2017):
    """
    Downloads all futures contracts for a specified symbol
    between a start year and a end year
    """
    contracts = construct_futures_symbols(symbol, start_year, end_year)
    for c in contracts:
        print('Downloading contract: %s' % c)
        download_contract_from_quandl(c, dl_dir)


if __name__ == '__main__':
    symbol = 'ES'

    # Make sure you've created this relative directory beforehand
    dl_dir = 'quandl/futures/ES'

    # Create the start and end years
    start_year = 2015
    end_year = 2017

    # Download the contracts into the directory
    download_historical_contracts(symbol, dl_dir, start_year, end_year)

    # Open up a single contract via read_csv
    es = pd.read_csv('%s/ESH2015.csv' % dl_dir, index_col='Date')
    es['Settle'].plot()
    plt.show()
