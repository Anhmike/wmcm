from __future__ import print_function

import datetime as dt
import pandas as pd
from pandas_datareader import data
import wmcm.functions as wmf

class stock(object):
    '''Core Stock Class
    Parameters:
    tic : (string) ticker symbol
    start : (string) beginning date of analysis period, in the format '%Y-%m-%d' (e.g. '2010-01-01')
    end : (string) ending date of analysis period, in the format '%Y-%m-%d' (e.g. '2012-12-31')
    interval : string, default 'd'
        Time interval code, valid values are 'd' for daily, 'w' for weekly,
        'm' for monthly and 'v' for dividend.
    '''

    # I'm not fucking with that @property shit. I try to keep it real
    def set_raw_prices(self, interval=self.interval):
        '''What does this function do?'''

        ## download history at specified interval; note that interval is defaulted to the class attribute
        ## but can be adjusted accordingly
        history = data.YahooDailyReader(self.ticker, self.start, self.end)
    
        assert interval in ['m','w','d','v'], "Passed 'interval' of {} is not a valid type.".format(interval)    

        ## set prices_raw, which is now a dictionary indexed by interval
        self.prices_raw[interval] = history.read()

        return None # this is not necessary but I find it helps remind me of the functions purpose

    def set_adj_prices(self, interval=self.interval):
        '''Get adjusted prices...'''

        assert interval in ['m','w','d','v'], "Passed 'interval' of {} is not a valid type.".format(interval)

        self.prices_adj[interval] = wmf.adjust_prices(self.prices_raw[interval]

        return None
    
    def returns_get(self, interval=self.interval):
        '''Function purpose?'''

        assert interval in ['m','w','d','v'], "Passed 'interval' of {} is not a valid type.".format(interval)

        self.returns[interval] = wmf.get_returns(self.prices_adj[interval])

        return None

    def __init__(self, tic, start='2010-01-01', end='2015-12-31', interval='m'):
        self.ticker = tic
        self.interval = interval
        self.start = dt.datetime.strptime(start, '%Y-%m-%d')
        self.end = dt.datetime.strptime(end, '%Y-%m-%d')
        self.set_raw_prices()
        self.set_adj_prices()
        self.returns_get()

    def __getitem__(self, key):
        return self.data[key]

    def __repr__(self):
        return '''Stock : {0}
        Starting Date : {1}
        Ending Date : {2}'''.format(self.ticker,self.start,self.end)
