#!/usr/bin/env python
# Author: Ava Lee

import argparse
import datetime
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import pickle
from unicodedata import normalize
import os

parser = argparse.ArgumentParser(description='Scrape stock headlines')
parser.add_argument('-t', "--ticker", dest='ticker', default='',
                    help='Stock ticker to obtain headlines for')
parser.add_argument('-w', "--website", dest='website', default='finviz', help='Website to scrape')
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


if __name__ == "__main__":
    if args.outdir[-1] != '/':
        outdir = args.outdir + '/'
    else:
        outdir = args.outdir
    if not (os.path.isdir(outdir)): os.makedirs(outdir)

    if args.ticker != '':
        scraper(args.ticker, outdir, args.website)
    else:
        scraper_all(outdir, args.website)