

"""
readme for risk_normalization

This file created on Tuesday, October 6, 2020

Risk normalization routines designed by Dr. Howard Bandy, 
Blue Owl Press.

License:  MIT

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

Assumptions
  A trade list has been created by some process.
    It could be live trades, validation trades, in-sample trades,
    or hypothetical trades.
  The trades represent the gain of a single day,
    such as the change in price from today's close to tomorrow's
    close.
A gain of 1% is represented as 0.0100
A day where the position is flat has a gain of 0.0000
There are about 252 trades per year
The account is marked to market daily.
The account is managed daily.
The trader is able and willing to change position daily.

Use:
  safe-f, CAR25 = risk_normalization(
                    trades,
                    sequence_length=504,
                    initial_capital=100000.0,
                    tail_percentage=5,
                    drawdown_tolerance=0.10,
                    number_equity_in_CDF=1000,
                  )

Parameters:
  trades:  The set of trades to evaluate.
      Expecting a numpy array with one dimension.
  sequence_length:  the forecast period.
      The number of trades to draw for each equity sequence
  initial_capital:  initial amount in the trading account.
      Default = $100,000.00
  tail_percentage:  The percentage at which to measure the
      tail risk.  Default = 5
  drawdown_tolerance:  The traders drawdown tolerance.
      Expressed as a proportion of maximum equity to date.
      Default = 0.10  A 10% drawdown.
  number_equity_in_CDF:  The number of equity curves used
      to compute a single CDF.  Default = 1000

Returns:
  safe-f:  The fraction of the trading account that will be
      used for each trade.
  CAR25:  The compound annual rate of return for the given
      set of trades and position size.


definitions of variables

drawdown:              list used to accumulate day by day drawdown
max_drawdown           maximum drawdown to date
equity:                list used to accumulate day by day equity
max_equity:            maximum equity to date

file_namne:            name of csv or txt file containing trades
fraction:              during calculations, the then current estimate
                        of position size, safe-f
initial_capital:       trading account allocated to this system in dollars
                        Typically 100000.0                 

number_days_in_forecast: 
                       number of days in forecast horizon  
                       Typically 500 for a 2 year forecast
number_repetitions:    
                       number of replications of calculation of 
                       safe-f and CAR25.  Typically 10.
number_sequences:
                       number of equity sequences used to form
                       the distribution.  Typically 1000.                    
number_trades_in_forecast: 
                       number of trades in each equity sequence 
                       Varies.  
                           Same as number_forecast_days if
                             marking to market and trading daily.
                           A smaller number if trade data
                             represents multiday holding.
number_trades_in_best_est:   
                       number of trades in best estimate set 
                       of trades --
                           read from file 
                           or drawn from known distribution 


"""