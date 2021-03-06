import datetime as dt
import pandas as pd
import numpy as np
from pandas_datareader import data

def adjust_prices(df):
    '''Adjusts df prices for dividends and splits.'''

    ## make a deep copy of the input data so we don't accidentally change it
    data = df.copy()

    ## Uses the observe difference between 'Close' and 'Adj Close' to adjust all fields.
    data['AdjFactor'] = data['Adj Close'] / data['Close']
    data['Open'] = data['Open'] * data['AdjFactor']
    data['High'] = data['High'] * data['AdjFactor']
    data['Low'] = data['Low'] * data['AdjFactor']
    data['Close'] = data['Close'] * data['AdjFactor']

    new_df = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    new_df.columns = ['open', 'high', 'low', 'close', 'volume']

    return new_df

def get_returns(df):
    '''Gets returns...'''

    ## make a deep copy of the input data so we don't accidentally change it
    data = df.copy()

    data['lastClose'] = data['close'].shift(1)
    data['ret_cc'] = np.log(data['close'] / data['lastClose']) # close to close return
    data['ret_oc'] = np.log(data['close'] / data['open']) # open to close return
    data['ret_co'] = np.log(data['open'] / data['lastClose']) # close to open return

    ## what is this for?
    data.drop('lastClose', 1, inplace=True)

    return data
