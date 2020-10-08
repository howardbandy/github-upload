# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 18:43:21 2019

risk_normalization.py

Risk normalization routines designed by Dr. Howard Bandy, 
Blue Owl Press.

This technique was originally published in the book,
"Modeling Trading System Performance," in 2011, as an 
Excel Add-in.
Published again in the book "Quantitative Technical Analysis,"
in 2014, as a Python program.

The risk normalization consits of two phases:
1.  Compute the maximum fraction of the trading account
    that can be used to take a position in the tradable issue
    without exceeding the personal risk tolerance of the
    trader.  This is called "safe-f"
2.  Using safe-f as a position size, compute the profit
    potential for the forecast period.  Convert the gain
    to Compound Annual rate of Return, called "CAR25"
    
Compute maximum safe position size based on risk of drawdown.
Given that position size, estimate the profit potential.
  
Each trader has a personal risk tolerance.  
Enter the parameters that define that tolerance.
  

Overview of the program:

Begin with a set of trades.  These are analyzed as is to compute
safe-f, and are assumed to be the best estimate of future 
performance.  This set does not change throughout the procedure.

Set the fraction an initial value of 1.00
    Create many equally likely equity curves,
        measure the maximum drawdown of each,
        keep them in a list.
    Treat the list of max drawdowns as a distribution
        and determine the maximum drawdown at the high
        risk tail -- probably at the 95th percentile.
    Compare the trader's personal risk tolerance with
        the tail risk of the distribution.
        If they are equal, the current value of the
        fraction is safe-f.
        If they are not equal, adjust the fraction and 
        repeat.

safe-f has been established.

Using safe-f as the fraction
    Create many equally likely equity curves,
        measure the final equity,
        keep that in a list.
    Treat the list of final equity as a distribution
        and determine the equity at the 25th percentile.
    Convert the relative gain in equity to a 
        compound annual rate of return.
        That value is car25.

Return safe-f and CAR25
  
"""

#  Assumptions
#    A trade list has been created by some process.
#      It could be live trades, validation trades, in-sample trades,
#      or hypothetical trades.
#    The trades represent the gain of a single day,
#      such as the change in price from today's close to tomorrow's
#      close.
#  A gain of 1% is represented as 0.0100
#  A day where the position is flat has a gain of 0.0000
#  There are about 252 trades per year
#  The account is marked to market daily.
#  The account is managed daily.
#  The trader is able and willing to change position daily.
#
#
#  Use:
#    safe-f, CAR25 = risk_normalization(
#                      trades,
#                      sequence_length=500,
#                      initial_capital=100000.0,
#                      tail_percentage=5,
#                      drawdown_tolerance=0.10,
#                      number_equity_in_CDF=1000,
#                      weighting='uniform'
#                    )
#
#  Parameters:
#    trades:  The set of trades to evaluate.
#        Expecting a numpy array with one dimension.
#    sequence_length:  the forecast period.
#        The number of trades to draw for each equity sequence
#    initial_capital:  initial amount in the trading account.
#        Default = $100,000.00
#    tail_percentage:  The percentage at which to measure the
#        tail risk.  Default = 5
#    drawdown_tolerance:  The traders drawdown tolerance.
#        Expressed as a proportion of maximum equity to date.
#        Default = 0.10  A 10% drawdown.
#    number_equity_in_CDF:  The number of equity curves used
#        to compute a single CDF.  Default = 1000
#    weighting:  Alternatively weight each trade the same or
#        weight recent trades more heavily.
#        Two weightings are included:  'uniform' and 'triangular'.
#        Default = 'uniform'
#
#  Returns:
#    safe-f:  The fraction of the trading account that will be
#        used for each trade.
#    CAR25:  The compound annual rate of return for the given
#        set of trades and position size.
#

# matplotlib inline
#%load_ext nb_black
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import seaborn as sns
import time


def make_trade_list( number_trades=1000,
                     mean_gain = 0.001,
                     std_dev = 0.003):
    
    trades = np.random.normal(mean_gain,
                              std_dev,
                              number_trades)
    
    file_name = 'trades.csv'
    np.savetxt(file_name, trades, delimiter=',')

    return (trades)



def generate_trade_list(number_trades, mu=0.001, sigma=0.003):

    """
    Generate a set of pseudo trades.
    Each trade is drawn from a normal distribution.
    
    Parameters:
    number_trades:  Desired size of the set of trades.
    mu:  Mean.
    sigmal:  standard deviation.
    
    Returns:
    s:  Numpy array containing the set of trades.
    
    """

    s = np.random.normal(mu, sigma, number_trades)

    return s


def make_one_equity_sequence(
    trades,
    fraction=1.0,
    forecast_length=500,
    initial_capital=100000.0,
    plot=False,
):

    """
    Given a set of trades, draw a random sequence of trades
    and form an equity sequence.
    
    Parameters:
    trades:  the set of trades to be analyzed
    fraction:  the proportion of the trading account
               to be used for each trade.
    sequence_length:  The length of the equity sequence.
    initial_capital:  Starting value of the trading account.
    weighting:  uniform -- all trades have equal weight
                triangular -- more recent trades have higher weight
    plot:  True will create and display a plot of the equity curve.    
    
    Returns:  
    Two scalars:
    equity:  The equity at the end of the sequence in dollars.
    max_drawdown:  The maximum drawdown experienced in the sequence
            as a proportion of highest equity marked to market
            after each trade.
    """

    pool_size = len(trades)

    #  set the weights

    #  If desired, form weighted trades.
    #  Default is 'uniform'
    #  No transformation is required
    #  Alternative is 'triangular'
    #  Oldest trade is in element 0
    #  Newest trade is in element number_trades

 

    #  initialize sequence

    equity = initial_capital
    max_equity = equity
    drawdown = 0.0
    max_drawdown = drawdown

    daily_equity = np.zeros(forecast_length)

    #  form sequence

    for i in range(forecast_length):
        trade_index = random.randint(0, pool_size - 1)
        trade = trades[trade_index]
        trade_dollars = equity * fraction * trade
        equity = equity + trade_dollars
        daily_equity[i] = equity
        max_equity = max(equity, max_equity)
        drawdown = (max_equity - equity) / max_equity
        max_drawdown = max(drawdown, max_drawdown)

    if plot:
        plt.plot(daily_equity)
        plt.show()

    #  return

    return (equity, max_drawdown)


def analyze_distribution_of_drawdown(
    trades,
    fraction=1.0,
    forecast_length=500,
    initial_capital=100000.0,
    weighting="uniform",
    number_sequences=1000,
    tail_percentile=5,
):

    """
    
    Returns:
    sorted_max_dd:  A numpy array of maximum drawdown
                    for the equity curves formed from
                    the trades provided.
    """
    equity_list = []
    max_dd_list = []

    for i in range(number_sequences):
        equity, max_drawdown = make_one_equity_sequence(trades, fraction)
        equity_list.append(equity)
        max_dd_list.append(max_drawdown)

    sorted_max_dd = np.sort(max_dd_list)
    plt.plot(sorted_max_dd)
    plt.show()

    tail_risk = np.percentile(sorted_max_dd, 100 - tail_percentile)

    return tail_risk


def compute_tail_risk(drawdowns, fraction=1.00, tail_percentile=5):

    """
    Given a set of maximum drawdowns,
    and the fraction of the trading account allocated to trades,
    compute the drawdown at the tail of the distribution.
    
    Parameters:
    drawdowns:  The set of maximum drawdowns.
    fraction:  The fraction of the account allocated to trades.
    tail_percentile:  The percentile (from the high end) at which 
        to measure. 
    
    Returns:
    tail_risk:  The maximum drawdown at the tail of the distribution.
    """

    CDF_dd = np.asarray(analyze_distribution_of_drawdown(drawdowns, fraction))
    tail_risk = np.percentile(CDF_dd, 100 - tail_percentile)

    return tail_risk


def form_distribution_of_equity(
    trades,
    fraction=1.0,
    forecast_length=500,
    initial_capital=100000.0,
    number_sequences=1000,
):
    equity_list = []
    max_dd_list = []

    for i in range(number_sequences):
        equity, max_drawdown = make_one_equity_sequence(trades, fraction)
        equity_list.append(equity)
        max_dd_list.append(max_drawdown)

    sorted_equity = np.sort(equity_list)
    plt.plot(sorted_equity)
    plt.show()

    return sorted_equity


#######  Program begins
#
#  The set of trades can come from any process --
#    backtest, walk forward, paper trade, live trades.
#  Typically, they will be read from a csv file that was
#    created by some trading system.
#
#  In this example, they are drawn from a Normal distribution.
#

########## Generate a set of trades drawn from a Normal distribution
#    
#  Generate trades for analysis

number_trades = 1000  #  number of days
mean_profit = 0.001  # 0.1% per trade
standard_dev = 0.003  # 0.3% per trade

#trades = make_trade_list(1000)
#print (trades)
##########

########## Read a text file containing the list of trades
#
#  Read trades for analysis

filename = 'trades.csv'
trades = np.read_csv(filename)
#print (trades)
##########

#  Set the parameters describing the personal risk tolerance
#  of the trader.

drawdown_tolerance = 0.10

desired_accuracy = 0.003

initial_capital=100000.0


for rep in range(5):

    #  Fraction is initially set to use all available funds
    #  It will be adjusted in response to the risk of drawdown.
    #  The final value of fraction is safe-f
    
    fraction = 1.00
    
    #  Generate distribution of max_drawdown
    
    tail_risk = analyze_distribution_of_drawdown(trades)
    
    #print(tail_risk)
    
    
    #  Solve for safe-f
    
    fraction = 1.0
    done = False
    while not done:
        print(f"fraction this pass:  {fraction:0.3f}")
        tail_risk = analyze_distribution_of_drawdown(trades, fraction)
    
        print(f"tail_risk this pass: {tail_risk:0.3f}")
        if abs(tail_risk - drawdown_tolerance) < desired_accuracy:
            #  done
            safe_f = tail_risk
            done = True
        else:
            fraction = fraction * drawdown_tolerance / tail_risk
    
    print(f'final value: safe_f: {fraction:0.3f}')
    
    #  Compute CAR25
    #  fraction == safe_f
    #  Compute CDF of equity
    #  CAR25 is 25th percentile
    
    forecast_length = 500
    
    CDF_equity = form_distribution_of_equity(trades, fraction=fraction)
    TWR25 = np.percentile(CDF_equity, 25)
    print(f'terminal wealth: {TWR25:9.0f}')
    
    CAR25 = 100.0 * (math.exp((252.0 / forecast_length) * 
                             math.log(TWR25/initial_capital)) - 1.0)
    print(f'Compound Annual Retrun: {CAR25:0.3f}%')

print("all done")
