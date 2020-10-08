#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_trade_list.py

Creates a list of trades and writes them to disk
The file can be read by the risk_normalization program

Created on Tue Sep 15 19:06:42 2020

@author: howard bandy
"""

import matplotlib.pyplot as plt
import numpy as np

def make_trade_list( number_trades=1000,
                     mean_gain = 0.001,
                     std_dev = 0.003):
    
    trades = np.random.normal(mean_gain,
                              std_dev,
                              number_trades)
    return (trades)

trades = make_trade_list(1000)
# print (trades)

file_name = 'trades.csv'
np.savetxt(file_name, trades, delimiter=',')

sorted_trades = np.sort(trades)

y_pos = np.arange(len(trades))

plt.bar(y_pos,sorted_trades)
plt.show()

##  End ##

