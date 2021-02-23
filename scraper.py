#!/usr/bin/env python
# Author: Ava Lee

import argparse
import datetime
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import pickle
from unicodedata import normalize

parser = argparse.ArgumentParser(description='Scrape stock headlines')
parser.add_argument('-t', "--ticker", dest='ticker', required=True,
                    help='Stock ticker to obtain headlines for')
parser.add_argument('-s', "--source", dest='source', default='finviz', help='News source to obtain data from')
args = parser.parse_args()


def scraper(ticker, source='finviz'):
    """ Based on https://blog.thecodex.me/sentiment-analysis-tool-for-stock-trading/"""
    if source == 'finviz':
        url = 'https://finviz.com/quote.ashx?t='
    
    url += ticker
    req = Request(url=url, headers={'user-agent': 'my-app'})
    response = urlopen(req)
    
    html = BeautifulSoup(response, features='html.parser')
    news_table = html.find(id='news-table')
    
    # Parse the HTML to obtain data
    parsed_data = []
    for row in news_table.findAll('tr'):
        title = row.a.text # Get headline
        
        # Get date and time
        date_data = row.td.text.split(' ') 
        if len(date_data) == 1:
            time = normalize('NFKD', date_data[0]).rstrip()
        else:
            date = date_data[0]
            time = normalize('NFKD', date_data[1]).rstrip()
        parsed_data.append([ticker, date, time, title])
    
    # Save the parsed data
    file = open(ticker + '_' + str(datetime.date.today()) + '.pkl', 'wb')
    pickle.dump(parsed_data, file)
    file.close()
    

if __name__ == "__main__":
    scraper(args.ticker, args.source)