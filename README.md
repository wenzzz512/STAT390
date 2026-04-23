## Evaluating SMT Divergence in the New York Session using Auto-Research
Objective: To evaluate the statistical reliability of SMT divergence and identify the parameter settings under which it provides a reliable leading signal for short-term price reversals using SPY and QQQ ETFs.

Data source: Polygon.io API  
Data: 2 years of SPY and QQQ intraday data (2024-04-01 to 2026-04-01), filtered to New York session (9:30 AM – 4:00 PM ET)

Primary Metric: Sharpe Ratio——risk-adjusted return(mean return / standard deviation, fixed)

Backtest: Historical simulation where trades are triggered by SMT signals, and returns are evaluated over a fixed future holding period.

SMT Logic: SMT divergence is defined as one asset making a higher high or lower low while the other fails to confirm. 
- Signals are evaluated based on their ability to predict future returns.

Parameter configurations (Editable by Agent): 
Lookback window (N swing definition): The number of past bars used to define local highs and lows for SMT detection   
Holding period (H) : Holding period (H): Number of bars a position is held after signal generation
Threshold (T): minimum divergence required between assets 

Working Baseline: 1-minute and 5-minute SMT strategies on SPY and QQQ


### System Design
prepare.py (frozen module)
- Data loading and preprocessing
- Time-based train/test split (time-based split to ensure only past information is used, preventing look-ahead bias)
- Fixed Sharpe ratio calculation
- Transaction cost parameter
- Ensures consistent evaluation across experiments

train.py (editable module)
- SMT detection logic
- Strategy execution and backtesting
- Parameter configurations (N, H, T)
- Timeframe selection (1m, 5m, both)
- Experiment logging (CSV output)
- Runtime measurement











