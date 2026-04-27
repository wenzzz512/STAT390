# AutoResearch Agent Instructions

## Objective 
Your goal is to improve the Sharpe ratio of an SMT divergence strategy applied to SPY and QQQ intraday data. 
You should search for parameter configurations and logic improvements that increase risk-adjusted returns.

---

## What you CAN change
You can ONLY modify `model.py`

---

## What you CANNOT change
The following files are frozen and must not be changed:
- `prepare.py` (data loading, evaluation, logging)
- `run.py` (execution pipeline)
- `experiment_log.csv` (results)
- any data files (train/test datasets)

---

## Strategy Description
The strategy is based on SMT divergence:
- One asset (SPY or QQQ) makes a higher high or lower low
- The other asset fails to confirm
- This divergence is used as a signal for potential reversal

---

## Parameters You Can Change
You may modify the following parameters in `model.py`:
- LOOKBACK (N): swing detection window
- HOLDING_1M (H): holding period for 1-minute data
- HOLDING_5M (H): holding period for 5-minute data
- T: divergence threshold
- TIMEFRAME_MODE: "1m", "5m", or "nested" (1m & 5m)

---

## Functions You Can Modify
You may modify:
- detect_swings()
- detect_smt()

You may improve:
- signal quality
- filtering logic
- definition of swings
- divergence conditions

---

## Nested Strategy Option

You may implement a nested multi-timeframe strategy.

Nested SMT means:
- Use 1-minute SMT signals as entry signals
- Use 5-minute SMT structure as confirmation

Examples:
- Only take 1m bullish SMT when 5m structure supports bullish reversal
- Only take 1m bearish SMT when 5m structure supports bearish reversal

Goal:
- Reduce noise from 1m signals
- Improve signal quality and Sharpe ratio

---

## Evaluation Metric

Performance is evaluated using:
- Sharpe Ratio (defined in prepare.py)
- Higher Sharpe is better

---

## How to Run

To evaluate a strategy:

```bash
python run.py
