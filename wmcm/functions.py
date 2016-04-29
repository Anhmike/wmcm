import datetime as dt
import pandas as pd
import numpy as np
from pandas_datareader import data


def greg():
 print('Fuck off!')

def adjust_prices(df):
    '''Adjusts df prices for dividends and splits.'''
    df['AdjFactor'] = df['Adj Close'].shift(1) / df['Close'].shift(1)
    df['Open'] = df['Open'] * df['AdjFactor']
    df['High'] = df['High'] * df['AdjFactor']
    df['Low'] = df['Low'] * df['AdjFactor']
    df['Close'] = df['Close'] * df['AdjFactor']
    new_df = df[['sector', 'symbol', 'Open', 'High', 'Low', 'Close', 'Volume']]
    new_df.columns = ['sector', 'symbol', 'open', 'high', 'low', 'close', 'volume']
    return new_df

def get_returns(df):
    df['lastClose'] = df['close'].shift(1)
    df['ret_cc'] = np.log(df['close'] / df['lastClose'])
    df['ret_oc'] = np.log(df['close'] / df['open'])
    df['ret_co'] = np.log(df['open'] / df['lastClose'])
    df.drop('lastClose', 1, inplace=True)
    return df