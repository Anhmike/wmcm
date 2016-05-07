import datetime as dt
import pandas as pd
from pandas_datareader import data
import warnings
import math

from wmcm.core.Market import Market
import wmcm.functions as wmf

def _warning(message, category = UserWarning, filename = '', lineno = -1):
    print(message)

warnings.showwarning = _warning

class Portfolio(Market):
    '''Core Portfolio Class
    Used within backtests to track current holdings.
    Parameters:
    capital : starting portfolio balance
    '''

    def __init__(self, capital):
        self.holdings = pd.DataFrame(columns=['security','quantity', 'price', 'market_value'])
        self.holdings.set_index('security', inplace=True)
        self.holdings.loc['str8cash', 'quantity'] = capital
        self.holdings.loc['str8cash', 'price'] = 1
        self.update_value()

    def total_value(self):
        self.update_value()
        return sum(self.holdings['market_value'])

    def update_value(self):
        self.holdings['market_value'] = self.holdings['quantity'] * self.holdings['price']


    def update_prices(self, universe, date, type='close'):
        '''Updates .holdings prices for a given date.
        type : string, default 'close.' Also available: open, high, low
        '''
        # Ensure we are starting with a day where the market was open.
        # If not, subtract days until we are.
        # Running on a Sunday will give us Friday's closing price.
        applied_date = date
        while applied_date not in universe['market'].adj_prices.index:
            applied_date -= dt.timedelta(days=1)

        # Convert to string for indexing
        string_date = applied_date.strftime('%Y-%m-%d')

        for tic in self.holdings.index:
            if tic == 'str8cash':
                continue
            self.holdings.loc[tic, 'price'] = universe[tic].adj_prices.loc[string_date, type]

        self.update_value()

    def open_position(self, tic, price, target_percent):
        '''Opens a new position. Assumes there are currently no holdings.
        tic : (string) ticker symbol
        price : Effective price
        target_percent : percent of portfolio to invest in a given ticker.
        '''

        self.holdings.loc[tic] = [0, price, 0]

        target_value = target_percent * self.total_value()
        target_q = target_value / self.holdings.loc[tic, 'price']
        
        order_q = math.floor(target_q)
        order_value = order_q * self.holdings.loc[tic, 'price']

        self.holdings.loc['str8cash', 'quantity'] -= order_value
        self.holdings.loc[tic, 'quantity'] += order_q
        self.update_value()

    def close_position(self, tic, price):
        '''Closes an existing position.
        tic : (string) ticker symbol
        price : Effective price
        '''
        self.holdings.loc[tic, 'price'] = price
        self.update_value()
        order_value = self.holdings.loc[tic, 'market_value']
        self.holdings.loc['str8cash', 'quantity'] += order_value

        self.holdings.drop(tic, inplace=True)
        self.update_value()