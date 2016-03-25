import datetime as dt

class stock(object):
 '''Core Stock Class
 Parameters:
 tic : string containing Ticker symbol
 start : (string) beginning date of analysis period, in the format '%Y-%m-%d' (e.g. '2010-01-01')
 end : (string) ending date of analysis period, in the format '%Y-%m-%d' (e.g. '2012-12-31')
 '''

 def __init__(self, tic, start='2010-01-01', end='2012-09-20'):
  if tic is None:
   tic='SPY'
  assert type('SPY')==str, 'Ticker must be a string.'
 
  self.ticker = tic.strip()
  self.start = dt.datetime.strptime(start, '%Y-%m-%d')
  self.end = dt.datetime.strptime(end, '%Y-%m-%d')

 def __repr__(self):
  return '''Stock : {0}
Starting Date : {1}
Ending Date : {2}'''.format(self.ticker,
					self.start,
					self.end)
