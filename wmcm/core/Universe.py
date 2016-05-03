from wmcm.core.Stock import Stock
from wmcm.core.Market import Market

import pickle
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
    >> newUni = wmcm.Universe.load('dickbutt.p')
    >> newUni.keys()
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

    def __init__(self, tics, market, start='2011-01-01', end='2015-12-31', interval='m', verbose=True):

        self.verbose = verbose
        self._print('Loading the Market {}...'.format(market))
        self['market'] = Market(market, start=start, end=end, interval=interval)

        for tic in tics:
            self._print('Loading {}...'.format(tic))
            try:
                self[tic] = Stock(tic, start=start, end=end, interval=interval)
            except ValueError:
                warnings.warn('ValueError occured for {}'.format(tic))
            except:
                warnings.warn('Some other Error occured for {}'.format(tic))
