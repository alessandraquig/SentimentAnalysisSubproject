import pandas as pd
import datetime
import pickle


def load_news_df(ticker, date=['2020-01-01', '2021-03-05'], indir='parsed_data', website="finnhub"):
    if isinstance(date, list):
        date_from = date[0]
        date_to = date[1]
        file = open(f'{indir}/{ticker}_{date_from}_{date_to}_{website}.pkl', 'rb')
    else:
        file = open(f'{indir}/{ticker}_{date}_{website}.pkl', 'rb')
    df = pickle.load(file)
    file.close()
    
    if website == 'finviz':
        df = pd.DataFrame(df, columns=['datetime', 'ticker', 'title', 'source']).set_index('timestamp', drop=True)

    return df


def load_price_df(ticker, date, window=None, interval='5min', indir='parsed_data', website="alphavantage"):
    if window != None:
        file = open(f'{indir}/{ticker}_{date}_{window}_{interval}_{website}.pkl', 'rb')
    else:
        file = open(f'{indir}/{ticker}_{date}_{interval}_{website}.pkl', 'rb')
    df = pickle.load(file)
    file.close()
    
    return df

    
    
    
    
