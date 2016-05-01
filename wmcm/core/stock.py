import datetime as dt
import pandas as pd
from pandas_datareader import data
import warnings

from wmcm.core.market import Market
import wmcm.functions as wmf

class Stock(Market):
    '''Core Stock Class
    Parameters:
    tic : (string) ticker symbol
    start : (string) beginning date of analysis period, in the format '%Y-%m-%d' (e.g. '2010-01-01')
    end : (string) ending date of analysis period, in the format '%Y-%m-%d' (e.g. '2012-12-31')
    interval : string, default 'd'
        Time interval code, valid values are 'd' for daily, 'w' for weekly,
        'm' for monthly and 'v' for dividend.
    '''

    def get_earnings(self):
        '''Function for retrieving earnings dates for the given stock.'''
        data = pd.read_csv('http://mt.tl/eps.php?symbol={}'.format(self.ticker))
        if len(data)<1:
            warnings.warn("No Earnings Data found!") 
        return data 

    def add_dates(self):
        '''Adds a column giving the end date for a given return df.'''
        self.adj_returns['start_date'] = self.adj_returns.index
        self.adj_returns['end_date'] = self.adj_returns.index
        self.adj_returns['end_date'] = self.adj_returns['end_date'].shift(-1)
        self.adj_returns['end_date'] = self.adj_returns['end_date'] - dt.timedelta(days=1)
        self.adj_returns.ix[-1, 'end_date'] = self.end

    def add_earnings(self):
        '''True if earnings date in period, False if earnings date not in period'''
        self.adj_returns['earnings_week'] = False #initialize false
        for eDate in self.earnings_dates:
            period_vector = ((self.adj_returns['end_date'] >= eDate) & (eDate >= self.adj_returns['start_date']))
            self.adj_returns['earnings_week'] = (self.adj_returns['earnings_week'] | period_vector)


    def __init__(self, tic, start='2011-01-01', end='2015-12-31', interval='m'):
        self.ticker = tic
        self.interval = interval
        self.start = dt.datetime.strptime(start, '%Y-%m-%d')
        self.end = dt.datetime.strptime(end, '%Y-%m-%d')
        self.raw_prices = self.generate_raw_prices(self.interval)
        self.adj_prices = wmf.adjust_prices(self.raw_prices)
        self.adj_returns = wmf.get_returns(self.adj_prices)
        self.add_dates()
        self.earnings_df = self.get_earnings()
        self.earnings_dates = self.earnings_df['date']
        self.add_earnings()

    def __repr__(self):
        return '''Stock : {0}
        Starting Date : {1}
        Ending Date : {2}
        Frequency : {3}'''.format(self.ticker, self.start, self.end, self.interval)
