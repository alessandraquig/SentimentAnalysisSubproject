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
