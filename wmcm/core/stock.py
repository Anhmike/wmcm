class stock(object):
 '''Core Stock Class
 Parameters:
 tic : string containing Ticker symbol'''
 def __init__(self, tic):
  if tic is None:
   tic='SPY'
  self.ticker = tic
