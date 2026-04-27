import time
import pandas as pd

from prepare import (
    sharpe_ratio,
    init_experiment_log,
    log_experiment,
    TRANSACTION_COST,
)

from model import (
    LOOKBACK,
    T,
    HOLDING_1M,
    HOLDING_5M,
    detect_swings,
    detect_smt,
)


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def get_returns(df: pd.DataFrame, holding: int) -> pd.Series:
    out = df.copy()

    out["future_close"] = out["SPY_Close"].shift(-holding)

    bullish_ret = (out["future_close"] - out["SPY_Close"]) / out["SPY_Close"]
    bearish_ret = (out["SPY_Close"] - out["future_close"]) / out["SPY_Close"]

    if TRANSACTION_COST != 0.0:
        cost = 2 * TRANSACTION_COST / out["SPY_Close"]
        bullish_ret = bullish_ret - cost
        bearish_ret = bearish_ret - cost

    returns = pd.concat([
        bullish_ret[out["bullish_smt"]],
        bearish_ret[out["bearish_smt"]],
    ]).dropna()

    return returns


def run(path: str, label: str, timeframe: str, holding: int):
    start = time.time()

    df = load_data(path)
    df = detect_swings(df, LOOKBACK)
    df = detect_smt(df, T)

    returns = get_returns(df, holding)

    sharpe = sharpe_ratio(returns, timeframe=timeframe)

    runtime = time.time() - start

    log_experiment(label, LOOKBACK, holding, T, sharpe, len(returns), runtime)

    print(f"{label}")
    print(f"signals: {len(returns)}")
    print(f"sharpe: {sharpe}")
    print(f"runtime: {runtime:.2f}s")


def main():
    init_experiment_log()

    run("train_1m.csv", "Baseline 1m", "1m", HOLDING_1M)
    run("train_5m.csv", "Baseline 5m", "5m", HOLDING_5M)


if __name__ == "__main__":
    main()