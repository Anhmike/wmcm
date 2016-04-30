from __future__ import print_function

import datetime as dt
import pandas as pd
from pandas_datareader import data
import wmcm.functions as wmf

class stock(object):
    '''Core Stock Class
    Parameters:
    tic : string containing Ticker symbol
    start : (string) beginning date of analysis period, in the format '%Y-%m-%d' (e.g. '2010-01-01')
    end : (string) ending date of analysis period, in the format '%Y-%m-%d' (e.g. '2012-12-31')
    interval : string, default 'd'
        Time interval code, valid values are 'd' for daily, 'w' for weekly,
        'm' for monthly and 'v' for dividend.
    '''

    ## just for the learning experience, creating a "read-only" ticker property
    ## if I wanted to make more properties read-only, could further decorate
    @property
    def ticker(self):
        return self._ticker

    @ticker.setter
    def ticker(self, value):
        try:
            print('Attribute already set : {}'.format(self._ticker))
        except AttributeError:
            self._ticker = value

    # I'm not fucking with that @property shit. I try to keep it real, n-word.
    def get_raw_prices(self, start, end, interval = 'm'):
        history = data.YahooDailyReader(self.ticker, start = start, end = end, interval = interval)
        # Need to add assertion here that interval is m, w, d or v.
        if interval == 'm':
            self.prices.raw.m = history.read()
        elif interval == 'w':
            self.prices.raw.w = history.read()
        elif interval == 'd':
            self.prices.raw.d = history.read()
        elif interval == 'v':
            self.prices.raw.v = history.read()

    def get_adj_prices(self, interval = 'm'):
        # Need to add assertion here that interval is m, w, d or v.
        if interval == 'm':
            self.prices.adj.m = wmf.adjust_prices(self.prices.raw.m)
        elif interval == 'w':
            self.prices.adj.w = wmf.adjust_prices(self.prices.raw.w)
        elif interval == 'd':
            self.prices.adj.d = wmf.adjust_prices(self.prices.raw.d)
        elif interval == 'v':
            self.prices.adj.v = wmf.adjust_prices(self.prices.raw.v)
    
    def returns_get(self, interval = 'm'):
        # Need to add assertion here that interval is m, w, d or v.
        if interval == 'm':
            self.returns.m = wmf.get_returns(self.prices.adj.m)
        elif interval == 'w':
            self.returns.w = wmf.get_returns(self.prices.adj.w)
        elif interval == 'd':
            self.returns.d = wmf.get_returns(self.prices.adj.d)
        elif interval == 'v':
            self.returns.v = wmf.get_returns(self.prices.adj.v)


    def __init__(self, tic, start='2010-01-01', end='2015-12-31', interval='m'):
        self.ticker = tic
        self.start = dt.datetime.strptime(start, '%Y-%m-%d')
        self.end = dt.datetime.strptime(end, '%Y-%m-%d')
        self.get_raw_prices(self, start=start, end=end, interval=interval)
        self.get_adj_prices(self, interval=interval)
        self.returns_get(self, interval=interval)

    def __getitem__(self, key):
        return self.data[key]

    def __repr__(self):
        return '''Stock : {0}
        Starting Date : {1}
        Ending Date : {2}'''.format(self.ticker,self.start,self.end)