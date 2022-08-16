import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly as px
from fredapi import Fred

fred = Fred('[my_FRED_API]')

class simple_backtest():
    
    def __init__(self, ma = 60, start = '1971-02-05', end = '2022-08-11'):
        self.ma = ma
        self.start = start
        self.end = end
        self.get_data()
        
    def get_data(self):
        self.data = fred.get_series('NASDAQCOM')
        self.data = pd.DataFrame({'Price': self.data})
        self.data.reset_index(inplace = True)
        self.data.rename(columns = {'index': 'Date'}, inplace = True)
        self.data['Date'] = self.data['Date'].apply(lambda x: str(x.date()))
        self.data.dropna(inplace = True)
        self.data = self.data.iloc[np.where(self.data['Date'] == self.start)[0][0]:np.where(self.data['Date'] == self.end)[0][0]]
        self.data['MA'] = self.data['Price'].rolling(self.ma).mean()
        self.data.dropna(inplace = True)
        self.data['Return'] = np.log(self.data['Price']/self.data['Price'].shift(1))
        self.data.dropna(inplace = True)
    
    def run_backtest(self):
        self.test = self.data.copy(deep = True)
        self.test['Position'] = np.where(self.test['Price'] > self.test['MA'], 1, -1)
        self.test['Strat'] = self.test['Return'] * self.test['Position'].shift(1)
        self.test.dropna(inplace = True)
        self.test['StratReturn'] = self.test['Strat'].cumsum().apply(np.exp)
        self.test['NormReturn'] = self.test['Return'].cumsum().apply(np.exp)
        
    def view_results(self):
        fig = go.Figure()
        for Return in self.test.columns[-2:]:
            fig.add_trace(go.Scatter(x = self.test['Date'], y = self.test[Return],
                                     mode = 'lines', name = Return))
        fig.show()
        
    def max_drawdown(self):
        self.ddowns = np.array([0])
        self.currentMinReturn = 1
        self.currentMaxReturn = 1
        for Return in self.test['StratReturn'][1:]:
            if Return > self.currentMaxReturn:
                self.ddowns = np.append(self.ddowns, 0)
                self.currentMaxReturn = Return
            else:
                self.ddowns = np.append(self.ddowns, ((Return - self.currentMaxReturn)/self.currentMaxReturn)*100)
                self.currentMinReturn = Return
        
        fig_DDown = go.Figure()
        fig_DDown.add_trace(go.Scatter(x = self.test['Date'], y = self.ddowns))
        fig_DDown.show()
        
    def sharpe(self):
        return np.mean(self.test['StratReturn'])/np.std(self.test['StratReturn'])
        # Should also add a rolling sharpe ratio.
       
## Example input:
# example = simple_backtest(15, '2003-11-05')
# example.run_backtest()
# example.view_results()
# example.max_drawdown()
# example.sharpe()
