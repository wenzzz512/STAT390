import pandas as pd
import numpy as np


LOOKBACK = 10
T = 0.01

HOLDING_1M = 10
HOLDING_5M = 2


def detect_swings(df: pd.DataFrame, lookback: int) -> pd.DataFrame:
    out = df.copy()

    out["SPY_swing_high"] = (
        out["SPY_High"] > out["SPY_High"].rolling(lookback).max().shift(1)
    )
    out["QQQ_swing_high"] = (
        out["QQQ_High"] > out["QQQ_High"].rolling(lookback).max().shift(1)
    )

    out["SPY_swing_low"] = (
        out["SPY_Low"] < out["SPY_Low"].rolling(lookback).min().shift(1)
    )
    out["QQQ_swing_low"] = (
        out["QQQ_Low"] < out["QQQ_Low"].rolling(lookback).min().shift(1)
    )

    return out


def detect_smt(df: pd.DataFrame, t: float) -> pd.DataFrame:
    out = df.copy()

    out["SPY_last_high"] = out["SPY_High"].where(out["SPY_swing_high"]).ffill()
    out["QQQ_last_high"] = out["QQQ_High"].where(out["QQQ_swing_high"]).ffill()

    out["SPY_last_low"] = out["SPY_Low"].where(out["SPY_swing_low"]).ffill()
    out["QQQ_last_low"] = out["QQQ_Low"].where(out["QQQ_swing_low"]).ffill()

    out["SPY_prev_high"] = out["SPY_last_high"].shift(1)
    out["QQQ_prev_high"] = out["QQQ_last_high"].shift(1)

    out["SPY_prev_low"] = out["SPY_last_low"].shift(1)
    out["QQQ_prev_low"] = out["QQQ_last_low"].shift(1)

    spy_high_move = (out["SPY_last_high"] - out["SPY_prev_high"]) / out["SPY_prev_high"]
    qqq_high_move = (out["QQQ_last_high"] - out["QQQ_prev_high"]) / out["QQQ_prev_high"]

    spy_low_move = (out["SPY_last_low"] - out["SPY_prev_low"]) / out["SPY_prev_low"]
    qqq_low_move = (out["QQQ_last_low"] - out["QQQ_prev_low"]) / out["QQQ_prev_low"]

    high_div = (spy_high_move - qqq_high_move).abs()
    low_div = (spy_low_move - qqq_low_move).abs()

    out["bearish_smt"] = (
        (
            (out["SPY_last_high"] > out["SPY_prev_high"]) &
            (out["QQQ_last_high"] <= out["QQQ_prev_high"]) &
            (high_div >= t)
        ) |
        (
            (out["QQQ_last_high"] > out["QQQ_prev_high"]) &
            (out["SPY_last_high"] <= out["SPY_prev_high"]) &
            (high_div >= t)
        )
    )

    out["bullish_smt"] = (
        (
            (out["SPY_last_low"] < out["SPY_prev_low"]) &
            (out["QQQ_last_low"] >= out["QQQ_prev_low"]) &
            (low_div >= t)
        ) |
        (
            (out["QQQ_last_low"] < out["QQQ_prev_low"]) &
            (out["SPY_last_low"] >= out["SPY_prev_low"]) &
            (low_div >= t)
        )
    )

    out["bearish_smt"] = out["bearish_smt"] & (
        ~out["bearish_smt"].shift(1).fillna(False)
    )
    out["bullish_smt"] = out["bullish_smt"] & (
        ~out["bullish_smt"].shift(1).fillna(False)
    )

    return out


