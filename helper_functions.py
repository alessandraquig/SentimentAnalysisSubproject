import pandas as pd
import datetime

def price_timestamp(df):
    """ Add new column to df to get corresponding price e.g. weekend dates to Friday 6pm,
    after 6pm to 6pm, before 9am to 6pm the day before - reflect Robinhood trading prices"""
    df['price_ts'] = df.index.round('5min')

    weekend = df['price_ts'].dt.dayofweek.isin([5, 6])
    df['price_ts'] = df['price_ts'].mask(weekend, (df['price_ts'] + pd.offsets.Week(n=0, weekday=6)
                                         - pd.DateOffset(2)).dt.normalize() + datetime.timedelta(hours=18))

    df['price_ts'] = df['price_ts'].mask(df['price_ts'].dt.hour > 18,
                                         df['price_ts'].dt.normalize() + datetime.timedelta(hours=18))
    df['price_ts'] = df['price_ts'].mask(df['price_ts'].dt.hour < 9, (df['price_ts']- pd.DateOffset(1)).dt.normalize()
                                         + datetime.timedelta(hours=18))

    return df


def load_news_df(ticker, date=['2020-01-01', '2021-03-05'], indir='parsed_data', website="finnhub"):
    if isinstance(date, list):
        file = open(f'{indir}/{ticker}_{date_from}_{date_to}_{website}.pkl', 'rb')
    else:
        file = open(f'{indir}/{ticker}_{date}_{website}.pkl', 'rb')
    data = pickle.load(file)
    file.close()
    
    if website == 'finviz':
        df = pd.DataFrame(data, columns=['timestamp', 'ticker', 'title', 'source']).set_index('timestamp', drop=True)

    return df


def load_price_df(ticker, date, window=None, indir='parsed_data', website="alphavantage"):
    if window != None:
        file = open(f'{indir}/{ticker}_{date}_{window}_{interval}_{website}.pkl', 'rb')
    else:
        file = open(f'{indir}/{ticker}_{date}_{interval}_{website}.pkl', 'rb')
    df = pickle.load(file)
    file.close()
    
    return df