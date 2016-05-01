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

    # I'm not fucking with that @property shit. I try to keep it real, n-word.
    def get_raw_prices(self):
        history = data.YahooDailyReader(self.ticker, self.start, self.end, interval=self.interval)
        # Need to add assertion here that interval is m, w, d or v.
        if self.interval == 'm':
            self.prices_raw_m = history.read()
        elif self.interval == 'w':
            self.prices_raw_w = history.read()
        elif self.interval == 'd':
            self.prices_raw_d = history.read()
        elif self.interval == 'v':
            self.prices_raw_v = history.read()

    def get_adj_prices(self):
        # Need to add assertion here that interval is m, w, d or v.
        if self.interval == 'm':
            self.prices_adj_m = wmf.adjust_prices(self.prices_raw_m)
        elif self.interval == 'w':
            self.prices_adj_w = wmf.adjust_prices(self.prices_raw_w)
        elif self.interval == 'd':
            self.prices_adj_d = wmf.adjust_prices(self.prices_raw_d)
        elif self.interval == 'v':
            self.prices_adj_v = wmf.adjust_prices(self.prices_raw_v)
    
    def returns_get(self):
        # Need to add assertion here that interval is m, w, d or v.
        if self.interval == 'm':
            self.returns_m = wmf.get_returns(self.prices_adj_m)
        elif self.interval == 'w':
            self.returns_w = wmf.get_returns(self.prices_adj_w)
        elif self.interval == 'd':
            self.returns_d = wmf.get_returns(self.prices_adj_d)
        elif self.interval == 'v':
            self.returns_v = wmf.get_returns(self.prices_adj_v)


    def __init__(self, tic, start='2010-01-01', end='2015-12-31', interval='m'):
        self.ticker = tic
        self.interval = interval
        self.start = dt.datetime.strptime(start, '%Y-%m-%d')
        self.end = dt.datetime.strptime(end, '%Y-%m-%d')
        self.get_raw_prices()
        self.get_adj_prices()
        self.returns_get()

    def __getitem__(self, key):
        return self.data[key]

    def __repr__(self):
        return '''Stock : {0}
        Starting Date : {1}
        Ending Date : {2}'''.format(self.ticker,self.start,self.end)