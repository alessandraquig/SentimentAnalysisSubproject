#!/usr/bin/env python
# Author: Ava Lee

import argparse
import datetime
import requests
import pandas as pd
import constants # API keys

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import pickle
from unicodedata import normalize
import os

parser = argparse.ArgumentParser(description='Get stock headlines or prices from webscraping or API')
parser.add_argument('-t', "--ticker", dest='ticker', default='', help='Stock ticker to obtain data for')
parser.add_argument('-w', "--website", dest='website', default='finnhub',
                    help='Website to scrape or get API from: finnhub (default), finviz, alphavantage')
parser.add_argument('-o', "--outdir", dest='outdir', default='parsed_data/', help='Output file directory')
args = parser.parse_args()


def scraper(ticker, outdir, website='finviz'):
    """ Based on https://blog.thecodex.me/sentiment-analysis-tool-for-stock-trading/"""
    if website == 'finviz':
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
        source = row.span.text # Get source of news

        # Get date and time
        date_data = row.td.text.split(' ') 
        if len(date_data) == 1:
            time = normalize('NFKD', date_data[0]).rstrip()
        else:
            date = date_data[0]
            time = normalize('NFKD', date_data[1]).rstrip()
        timestamp = datetime.datetime.strptime(date + ' ' + time, '%b-%d-%y %I:%M%p')
        
        parsed_data.append([timestamp, ticker, title, source])
    
    # Save the parsed data
    file = open(outdir + ticker + '_' + str(datetime.date.today()) + '_' + website + '.pkl', 'wb')
    pickle.dump(parsed_data, file)
    file.close()
    

def scraper_all(outdir, website='finviz'):
    if website == 'finviz':
        url = 'https://finviz.com/news.ashx'

    response = urlopen(req)
    html = BeautifulSoup(response, features='html.parser')
    news_table = html.find(id='news').select("table")[3].findAll('tr', {'class': 'nn'})

    parsed_data = []
    for news in news_table:
        content = news.text.strip().split('\n')
        time = datetime.datetime.strptime(content[0], '%I:%M%p')
        timestamp = datetime.datetime.combine(datetime.date.today(), time.time())
        title = content[1]

        parsed_data.append([timestamp, title])

    file = open(outdir + 'all_' + str(datetime.date.today()) + '_' + website + '.pkl', 'wb')
    pickle.dump(parsed_data, file)
    file.close()
    

def get_historical_news(ticker, date_from, date_to, outdir, website='finnhub'):
    data = {"symbol": ticker,
            "from": date_from,
            "to": date_to,
            "token": constants.FINNHUB_KEY} 
    
    response = requests.get('https://finnhub.io/api/v1/company-news', data)
    
    df = pd.DataFrame.from_dict(response.json()).drop(['category', 'id', 'image', 'url'], axis=1)
    df['datetime'] = pd.to_datetime(df['datetime'],unit='s')
    df = df.set_index('datetime')
    
    file = open(f'{outdir}/{ticker}_{date_from}_{date_to}_{website}.pkl', 'wb')
    pickle.dump(df, file)
    file.close()


if __name__ == "__main__":
    # Check output directory format
    if args.outdir[-1] != '/':
        outdir = args.outdir + '/'
    else:
        outdir = args.outdir
    if not (os.path.isdir(outdir)): os.makedirs(outdir)
        
    # Set dates to get historical data for
    date_from = '2020-01-01'
    date_to = '2021-03-05'
        
    # Web scrape or API
    if args.website == 'finviz':
        if args.ticker != '':
            scraper(args.ticker, outdir, args.website)
        else:
            scraper_all(outdir, args.website)
    if args.website == 'finnhub':
        if args.ticker == '':
            print ("Need to supply ticker in argument -t")
        else:
            get_historical_news(args.ticker, date_from, date_to, outdir)
        
        