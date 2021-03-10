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


def normalise_time(df_time_column):
    df_time_column = df_time_column.mask(df_time_column.dt.hour < 9,
                                         df_time_column.dt.normalize() + datetime.timedelta(hours=9))
    df_time_column = df_time_column.mask(df_time_column.dt.hour > 18,
                                         (df_time_column + pd.DateOffset(1)).dt.normalize()
                                         + datetime.timedelta(hours=9))
    
    weekend = df_time_column.dt.dayofweek.isin([5, 6])
    df_time_column = df_time_column.mask(weekend, (df_time_column + pd.offsets.Week(n=0, weekday=6)
                                         + pd.DateOffset(1)).dt.normalize() + datetime.timedelta(hours=9))
    
    return df_time_column
    

def price_timestamp(df):
    """ Add new column to df to get corresponding price e.g. weekend dates to Friday 6pm,
    after 6pm to 6pm, before 9am to 6pm the day before - reflect Robinhood trading prices"""
    df['price_ts'] = df.index.round('5min')
    df['price_ts'] = df['price_ts'].mask(df['price_ts'].dt.hour < 9,
                                         (df['price_ts'] - pd.DateOffset(1)).dt.normalize()
                                         + datetime.timedelta(hours=18))
    df['price_ts'] = df['price_ts'].mask(df['price_ts'].dt.hour > 18,
                                         df['price_ts'].dt.normalize() + datetime.timedelta(hours=18))
    
    weekend = df['price_ts'].dt.dayofweek.isin([5, 6])
    df['price_ts'] = df['price_ts'].mask(weekend, (df['price_ts'] + pd.offsets.Week(n=0, weekday=6)
                                         - pd.DateOffset(2)).dt.normalize() + datetime.timedelta(hours=18))

    return df


def get_prices(news_df, price_df):
    news_df['price'] = price_df.reindex(index=news_df['price_ts'])['Close'].astype(float).to_list()
    news_df['price_1d'] = price_df.reindex(index=normalise_time(news_df['price_ts']
                                        + pd.DateOffset(1)))['Close'].astype(float).to_list()
    news_df['price_1h'] = price_df.reindex(index=normalise_time(news_df['price_ts']
                                        + datetime.timedelta(hours=1)))['Close'].astype(float).to_list()
    #news_df['price_1w'] = price_df.reindex(index=normalise_time(news_df['price_ts']
    #                                   + datetime.timedelta(weeks=1)))['Close'].astype(float).to_list()

    
    return news_df
    
    
    
    