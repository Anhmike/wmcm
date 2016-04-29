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

    @property
    def bench(self, tic = 'SPY', start='2010-01-01', end='2012-09-20'):
        '''Creates benchmark portfolio.  Currently assumes SPY.'''
        return stock(tic, start = start, end = end)

    @bench.setter
    def bench(self, tic, start, end):
        self._bench = self.bench(tic, start, end)

    def __init__(self, tic, start='2010-01-01', end='2012-09-20', interval='d'):
        if tic is None:
            tic='SPY'
        assert type(tic)==str, 'Ticker must be a string.'
 
        self.ticker = tic.strip()
        self.start = dt.datetime.strptime(start, '%Y-%m-%d')
        self.end = dt.datetime.strptime(end, '%Y-%m-%d')
        self.raw = data.YahooDailyReader(tic, start = start, end = end, interval = interval).read()
        # self.adj = wmf.adjust_prices(self.raw)
        # self.returns = wmf.add_returns(self.adj)

    def __getitem__(self,key):
        return self.data[key]

    def __repr__(self):
        return '''Stock : {0}
        Starting Date : {1}
        Ending Date : {2}'''.format(self.ticker,self.start,self.end)

    def roll_beta(self, window = 60):
        '''Computes rolling beta against specified index.  Not sure how this should get returned.'''
        try:
            model = pd.ols(y = self['Close'], x = self.bench['Close'], window_type = 'rolling', window=window)
            return model
        except AttributeError:
            print("AttributeError: Need to specify your benchmark by setting the bench attribute in your stock.")

    def set_strategy(self, name, function):
        '''Ideally for a function which can operate on the rows of self.data, create a new attribute with strategy name.
        This setup would imply all relevant information should be hardcoded back into self.data (e.g., betas)
        Still need to consider how our backtesting / results summary will work before deciding what constraints to put on allowable functions.
        ========================
        Example Usage:
        >>> AAPL = wmcm.stock("AAPL")
        >>> AAPL.set_strategy("buy_everything", lambda : return 'BUY!')
        >>> AAPL.buy_everything()
        'BUY!' '''

        setattr(self, name, function)
