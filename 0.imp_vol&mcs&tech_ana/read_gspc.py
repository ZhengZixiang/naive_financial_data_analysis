# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_datareader.data as web

sp500 = web.DataReader('^GSPC', data_source='yahoo', start='1/1/2010', end='1/11/2018')
print(sp500.info())

sp500['Close'].plot(grid='True', figsize=(8, 5))
plt.show()

# 42天移动平均
sp500['42d'] = np.round(pd.Series(sp500['Close']).rolling(window=42).mean(), 2)  # 2保留两位小数
# 252天移动平均
sp500['252d'] = np.round(pd.Series(sp500['Close']).rolling(window=252).mean(), 2)
print(sp500[['Close', '42d', '252d']].tail())

sp500[['Close', '42d', '252d']].plot(grid='True', figsize=(8, 6))
plt.show()

sp500['42d-252d'] = sp500['42d'] - sp500['252d']
print(sp500['42d-252d'].tail())

S0 = 50
sp500['Regime'] = np.where(sp500['42d-252d'] > S0, 1, 0)
sp500['Regime'] = np.where(sp500['42d-252d'] < -S0, -1, sp500['Regime'])
print(sp500['Regime'].value_counts())

sp500['Regime'].plot(lw=1.5)
plt.ylim([-1.1, 1.1])
plt.show()

sp500['Market'] = np.log(sp500['Close'] / sp500['Close'].shift(1))
sp500['Strategry'] = sp500['Regime'].shift(1) * sp500['Market']
sp500[['Market', 'Strategry']].cumsum().apply(np.exp).plot(grid='True', figsize=(8, 6))
plt.show()
