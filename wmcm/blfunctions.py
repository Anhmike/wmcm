import wmcm
import math
import datetime as dt
import pandas as pd
import numpy as np
import statsmodels.formula.api as sm
import finsymbols
import pickle
import seaborn as sns
from pandas_datareader import data
import random

def dotheshuffle(df):
    new_index=list(df.index)
    random.shuffle(new_index)
    df=df.ix[new_index]
    df.reset_index()
    return df

def run_analysis(universe, excess=False, shuffle=False):

    if excess:
        GS20 = data.DataReader('GS20', 'fred', dt.datetime(2010, 11, 1), dt.datetime(2015, 12, 1))/100
        GS20.index = universe['market'].adj_returns.index

    universe['market'].analysis_df = universe['market'].adj_returns

    data_rows = len(universe['market'].analysis_df.index)

    for key in list(universe.keys()): # list(universe.keys()) allows you to delete while iterating
        if key == 'market':
            continue
        if len(universe[key].adj_returns.index) == data_rows: # Make sure stock alive through whole period.
            universe[key].analysis_df = universe[key].adj_returns
            universe[key].analysis_df = pd.merge(left = universe[key].analysis_df,
                                                 right = universe['market'].analysis_df,
                                                 left_index = True, right_index = True,
                                                 suffixes = ('', '_market'), how = 'left')

            if excess:
                universe[key].analysis_df['exc_ret_cc_market'] = universe[key].analysis_df['ret_cc_market'].subtract(GS20['GS20'])
                universe[key].analysis_df['exc_ret_cc'] = universe[key].analysis_df['ret_cc'].subtract(GS20['GS20'])

            universe[key].analysis_df['lag_ret_cc_market'] = universe[key].analysis_df['ret_cc_market'].shift(1)

            if excess:
                universe[key].analysis_df['lag_exc_ret_cc_market'] = universe[key].analysis_df['exc_ret_cc_market'].shift(1)

            universe[key].analysis_df = universe[key].analysis_df[2:] # Remove first two rows. With statsmodel 0.7.0, including nan's in train breaks predict

            if shuffle:
                universe[key].analysis_df['lag_ret_cc_market'] = dotheshuffle(universe[key].analysis_df['lag_ret_cc_market']).values
                if excess:
                    universe[key].analysis_df['lag_exc_ret_cc_market'] = dotheshuffle(universe[key].analysis_df['lag_exc_ret_cc_market']).values

            universe[key].model_sr = sm.ols('ret_cc ~ ret_cc_market',
                                            data=universe[key].analysis_df).fit()

            universe[key].model_mr = sm.ols('ret_cc ~ ret_cc_market + lag_ret_cc_market',
                                            data=universe[key].analysis_df).fit()

            if excess:
                universe[key].model_exc_sr = sm.ols('exc_ret_cc ~ exc_ret_cc_market',
                                                    data=universe[key].analysis_df).fit()
                universe[key].model_exc_mr = sm.ols('exc_ret_cc ~ exc_ret_cc_market + lag_exc_ret_cc_market',
                                                    data=universe[key].analysis_df).fit()

        else:
            del universe[key]

    return universe




def add_moving_forecasts(df):

    df = df[2:].copy()

    df['sample'] = 'test'
    df['sr_out_of_sample'] = np.nan
    df['mr_out_of_sample'] = np.nan

    for date in df.index:

        df.loc[:date, 'sample'] = 'train'
        df.loc[date, 'sample'] = 'test'

        try:
            sample_size = df['sample'].value_counts()['train']
        except:
            sample_size = 0

        if sample_size <= 30:
            continue
        else:
            moving_model_sr = sm.ols('ret_cc ~ ret_cc_market', data=df.loc[df['sample']=='train']).fit()
            df.ix[df['sample']=='test', 'sr_out_of_sample'] = moving_model_sr.predict(df.loc[df['sample']=='test'])
            moving_model_mr = sm.ols('ret_cc ~ ret_cc_market + lag_ret_cc_market', data=df.loc[df['sample']=='train']).fit()
            df.ix[df['sample']=='test', 'mr_out_of_sample'] = moving_model_mr.predict(df.loc[df['sample']=='test'])

    return df[['ret_cc', 'sr_out_of_sample', 'mr_out_of_sample']]

def score_moving_forecasts(df):

    df['sr_error'] = df['ret_cc'] - df['sr_out_of_sample']
    df['mr_error'] = df['ret_cc'] - df['mr_out_of_sample']

    df['sr_error_sq'] = np.square(df['sr_error'])
    df['mr_error_sq'] = np.square(df['mr_error'])

    df['sr_error_abs'] = np.absolute(df['sr_error'])
    df['mr_error_abs'] = np.absolute(df['mr_error'])

    return df

def backtest_stock(uni, tic, full_results=True, verbose=True):

    backtest_results = score_moving_forecasts(add_moving_forecasts(uni[tic].analysis_df))

    if verbose:
        print('Mean Forecast Error Squared w/o Lag Term: ' + str(backtest_results['sr_error_sq'].mean()))
        print('Mean Forecast Error Squared w/ Lag Term: ' + str(backtest_results['mr_error_sq'].mean()))
        print('Mean Absolute Forecast Error w/o Lag Term: ' + str(backtest_results['sr_error_abs'].mean()))
        print('Mean Absolute Forecast Error w/ Lag Term: ' + str(backtest_results['mr_error_abs'].mean()))

    if full_results:
        return backtest_results

def get_plot_data(uni):

    df = pd.DataFrame(index=uni.keys())
    df.drop('market', inplace=True)

    df['t_val'] = df.index.map(lambda x : uni[x].model_mr.tvalues[2])
    df['market_cap'] = df.index.map(lambda x : uni[x].market_cap)
    df['units'] = df['market_cap'].astype('str').str[-1:]
    df['market_cap'] = df['market_cap'].astype('str').str[:-1]

    df['new_units'] = np.nan
    df.loc[df['units'] == 'B', 'new_units'] = 1000000000
    df.loc[df['units'] == 'M', 'new_units'] = 1000000

    df['new_market_cap'] = pd.to_numeric(df['market_cap'], errors = 'coerce')

    df['new_market_cap'] = df['new_market_cap'] * df['new_units']

    df['market_cap'] = df['new_market_cap']
    df.drop(['units', 'new_units', 'new_market_cap'], axis = 1, inplace = True)
    df.columns = ['t_val', 'market_cap']

    # Additionally, let's add p values and AIC for both models.

    df['sr_bic'] = df.index.map(lambda x : uni[x].model_sr.bic)
    df['mr_bic'] = df.index.map(lambda x : uni[x].model_mr.bic)

    df['mr_p_values'] = df.index.map(lambda x : uni[x].model_mr.pvalues[2])
    df['mr_p_values_exc'] = df.index.map(lambda x : uni[x].model_exc_mr.pvalues[2])

    return df
