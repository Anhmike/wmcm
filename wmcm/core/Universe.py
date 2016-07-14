from wmcm.core.Stock import Stock
from wmcm.core.Market import Market

import pandas as pd
import numpy as np
import pickle
import statsmodels.formula.api as smf
import warnings

def _warning(message, category = UserWarning, filename = '', lineno = -1):
    print(message)

warnings.showwarning = _warning

class Universe(dict):
    '''Class for storing dictionaries of Stock objects, along with a Market object.
    Can be treated just like a dictionary, however it has a more convenient initialization.
    Moreover, Universe has save/load methods which pickle the resulting dictionary.

    Example:
    >>> import wmcm
    >>> Uni = wmcm.Universe(['GOOG','COF'], 'SPY')
    >>> Uni.save('dickbutt.p')
    >>> del Uni
    >>> newUni = wmcm.Universe.load('dickbutt.p')
    >>> newUni.keys()
    dict_keys(['GOOG', 'COF', 'market'])
    '''

    def _print(self, msg):
        if self.verbose:
            print(msg)

    def save(self, filename):
        '''Pickles Universe object into filename.'''
        pickle.dump(self, open(filename, 'wb'))

    @classmethod
    def load(cls, filename):
        '''Unpickles filename into new Universe instance.'''
        return pickle.load(open(filename, 'rb'))

    def factor_model_all(self, formula, filter_earnings=True):
        '''Runs factor_model() for every ticker in the universe'''
        self.results = {}
        for tic in self.keys():
            if tic=='market':
                pass
            else:
                try:
                    self.results[tic] = self.factor_model(tic, formula, filter_earnings = filter_earnings, env_lev=3)
                except ValueError:
                    self.results[tic] = np.nan
                except IndexError:
                    self.results[tic] = np.nan
                except KeyError:
                    self.results[tic] = np.nan

    def factor_model(self, tic, formula, filter_earnings=True, env_lev=2):
        '''Fits a standard factor model based on the given formula; searches for variables in Stock.analysis_df attribute
        which is USER-SET.  Will merge Stock with Market by Index.

        ANY NON-UNIQUE VARIABLE NAMES WHICH COME FROM THE MARKET SHOULD BE SUFFIXED AS SUCH!

        Example formula:
        return ~ return_market + lag(return)'''

        # create DataFrame
        data = pd.merge(left = self[tic].analysis_df, right = self['market'].analysis_df,
            left_index = True, right_index = True, suffixes = ('', '_market'), how = 'left')

        # filter earnings from DataFrame
        if filter_earnings:
            data = data.loc[(data['earnings_period'] == False)]

        # eval_env = 2 to look in the user's namespace for function definitions
        return smf.ols(formula, data=data, eval_env=env_lev).fit()

    def __init__(self, tics, market, start='2011-01-01', end='2015-12-31', interval='m', earn=True, verbose=True):

        self.verbose = verbose
        self._print('Loading the Market {}...'.format(market))
        self['market'] = Market(market, start=start, end=end, interval=interval)

        for tic in tics:
            self._print('Loading {}...'.format(tic))
            try:
                self[tic] = Stock(tic, start=start, end=end, interval=interval, earn=earn)
            except ValueError:
                warnings.warn('ValueError occured for {}'.format(tic))
            except:
                warnings.warn('Some other Error occured for {}'.format(tic))
