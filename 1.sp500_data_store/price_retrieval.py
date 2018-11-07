# -*- coding: utf-8 -*-
import re
import sys
import datetime
import calendar
import warnings
import MySQLdb as mdb
from urllib.request import urlopen, Request

db_host = 'localhost'
db_user = 'root'
db_pass = 'root'
db_name = 'quant'
con = mdb.connect(db_host, db_user, db_pass, db_name)


crumble_link = 'https://finance.yahoo.com/quote/{0}/history?p={0}'
crumble_regex = r'CrumbStore":{"crumb":"(.*?)"}'
cookie_regex = r'set-cookie: (.*?); '
quote_link = 'https://query1.finance.yahoo.com/v7/finance/download/'
quote_link += '%s?period1=%s&period2=%s&interval=1d&events=history&crumb=%s'


def obtain_list_of_db_tickers():
    """
    Obtains a list of the ticker symbols in the database
    """
    with con:
        cur = con.cursor()
        cur.execute('SELECT id, ticker FROM symbol')
        data = cur.fetchall()
        return [(d[0], d[1]) for d in data]


def get_crumble_and_cookie(symbol):
    """
    Reference the question page from stackoverflow to solve how to get crumb value:
    https://stackoverflow.com/questions/44044263/yahoo-finance-historical-data-downloader-url-is-not-working
    """
    link = crumble_link.format(symbol)
    response = urlopen(link)
    match = re.search(cookie_regex, str(response.info()))
    cookie_str = match.group(1)
    text = response.read().decode('utf-8')
    match = re.search(crumble_regex, text)
    crumble_str = match.group(1)
    return crumble_str, cookie_str


def get_daily_historic_data_yahoo(ticker, start_date='2015-01-01', end_date=datetime.date.today().isoformat()):
    """
    Obtains data from Yahoo Finance returns and a list of tuples
    :param ticker: Yahoo Finance ticker symbol, e.g. 'GOOG' for Google, Inc.
    :param start_date:  Start date in (YYYY, M, D) format
    :param end_date:  End date in (YYYY, M, D) format
    """
    # Construct the Yahoo URL with the correct integer query parameters
    # for start and end dates. Note that some parameters are zero-based!
    from_date = calendar.timegm((datetime.datetime.strptime(start_date, '%Y-%m-%d')-datetime.timedelta(days=1)).timetuple())
    to_date = calendar.timegm((datetime.datetime.strptime(end_date, '%Y-%m-%d')-datetime.timedelta(days=1)).timetuple())
    crumble_str, cookie_str = get_crumble_and_cookie(ticker)
    ticker_tuple = (ticker, from_date, to_date, crumble_str)
    yahoo_url = quote_link % ticker_tuple

    # Try connecting to Yahoo Finance and obtaining the data
    # On failure, print an error message
    try:
        request = Request(yahoo_url, headers={'Cookie': cookie_str})
        response = urlopen(request)
        text = response.read()
        yf_data = text.decode('utf-8').split('\n')[1:-1]
        prices = []
        for y in yf_data:
            p = y.strip().split(',')
            prices.append((datetime.datetime.strptime(p[0], '%Y-%m-%d'),
                          p[1], p[2], p[3], p[4], p[5], p[6]))
    except Exception as e:
        print('Could not download Yahoo data: %s' % e)
    return prices


def insert_daily_data_into_db(data_vendor_id, symbol_id, daily_data):
    """
    Takes a list of tuples of daily data and adds it to the MySQL database.
    Appends the vendor ID and symbol ID to the data.

    :param daily_data: List of tuples of the OHLC data (with adj_close and volume)
    """
    # Create the time now
    now = datetime.datetime.utcnow()

    # Amend the data to include the vendor ID and symbol ID
    daily_data = [(data_vendor_id, symbol_id, d[0], now, now,
                   d[1], d[2], d[3], d[4], d[5], d[6])
                  for d in daily_data]

    # Create the insert string
    column_str = 'data_vendor_id, symbol_id, price_date, created_date, last_updated_date, ' \
                 'open_price, high_price, low_price, close_price, volume, adj_close_price'
    insert_str = ('%s, ' * 11)[:-2]
    final_str = 'INSERT INTO daily_price (%s) VALUES (%s)' % (column_str, insert_str)

    # Using the MySQL connection, carry out an INSERT INTO for every symbol
    with con:
        cur = con.cursor()
        try:
            cur.executemany(final_str, daily_data)
        except Exception as e:
            print('INSERT NULL ERROR: %s' % e, file=sys.stderr)


if __name__ == '__main__':
    # This ignores the warnings regrading Data Truncation
    # from the Yahoo precision to Decimal(19,4) datatypes
    warnings.filterwarnings('ignore')

    # Loop over the tickers and insert the daily historical data into the database
    tickers = obtain_list_of_db_tickers()
    len_tickers = len(tickers)
    for i, t in enumerate(tickers):
        print('Adding data for %s: %s out of %s' % (t[1], i+1, len_tickers))
        attempts = 0
        while attempts < 10:
            try:
                yf_data = get_daily_historic_data_yahoo(t[1])
                insert_daily_data_into_db(1, t[0], yf_data)
                break
            except UnboundLocalError as error:
                continue
    print('Successfully added Yahoo Finance pricing data to DB')
