import pandas as pd
import numpy as np
import csv
import os

MASTER_FILE = "SPYQQQ_1m.csv"

TRAIN_1M_FILE = "train_1m.csv"
TEST_1M_FILE = "test_1m.csv"
TRAIN_5M_FILE = "train_5m.csv"
TEST_5M_FILE = "test_5m.csv"

SPLIT_DATE = "2025-07-01"

TRANSACTION_COST = 0.00
LOG_FILE = "experiment_log.csv"

REQUIRED_COLUMNS = [
    "timestamp",
    "SPY_Open",
    "SPY_High",
    "SPY_Low",
    "SPY_Close",
    "SPY_Volume",
    "QQQ_Open",
    "QQQ_High",
    "QQQ_Low",
    "QQQ_Close",
    "QQQ_Volume",
]

def load_master_data(filepath:str) -> pd.DataFrame:
    df = pd.read_csv(filepath)

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert("UTC")

    bad_ts = df["timestamp"].isna().sum()
    if bad_ts > 0:
        print(f"Dropping {bad_ts} rows with invalid timestamps")
        df = df.dropna(subset=["timestamp"])

    df = df.sort_values("timestamp").reset_index(drop=True)

    dup_count = df["timestamp"].duplicated().sum()
    if dup_count > 0:
        print(f"Dropping {dup_count} duplicate timestamp rows")
        df = df.drop_duplicates(subset=["timestamp"], keep="first")

    return df.reset_index(drop=True)

def split_train_test(df: pd.DataFrame, split_date: str):
    split_ts = pd.Timestamp(split_date, tz="UTC")

    train_df = df[df["timestamp"] < split_ts].copy()
    test_df = df[df["timestamp"] >= split_ts].copy()

    if train_df.empty:
        raise ValueError("Train set is empty. Choose an earlier SPLIT_DATE.")
    if test_df.empty:
        raise ValueError("Test set is empty. Choose a later SPLIT_DATE.")

    return train_df, test_df

def resample_to_5m(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.set_index("timestamp")

    agg_map = {
        "SPY_Open": "first",
        "SPY_High": "max",
        "SPY_Low": "min",
        "SPY_Close": "last",
        "SPY_Volume": "sum",
        "QQQ_Open": "first",
        "QQQ_High": "max",
        "QQQ_Low": "min",
        "QQQ_Close": "last",
        "QQQ_Volume": "sum",
    }

    df_5m = df.resample("5min").agg(agg_map).dropna().reset_index()
    return df_5m

def print_summary(full_df, train_1m, test_1m, train_5m, test_5m):
    print(f"Full 1m rows:  {len(full_df):,}")
    print(f"Train 1m rows: {len(train_1m):,}")
    print(f"Test 1m rows:  {len(test_1m):,}")
    print(f"Train 5m rows: {len(train_5m):,}")
    print(f"Test 5m rows:  {len(test_5m):,}")

    print("\nTime ranges:")
    print(f"Full:  {full_df['timestamp'].min()}  -->  {full_df['timestamp'].max()}")
    print(f"Train: {train_1m['timestamp'].min()}  -->  {train_1m['timestamp'].max()}")
    print(f"Test:  {test_1m['timestamp'].min()}  -->  {test_1m['timestamp'].max()}")

    train_max = train_1m["timestamp"].max()
    test_min = test_1m["timestamp"].min()

    print("\nOverlap check:")
    if train_max < test_min:
        print("PASS: train/test do not overlap.")
    else:
        print("WARNING: train/test may overlap.")

def main():
    print("Loading master file...")
    df = load_master_data(MASTER_FILE)

    print("Cleaning data...")
    df = clean_data(df)

    print("Splitting train/test...")
    train_1m, test_1m = split_train_test(df, SPLIT_DATE)

    print("Resampling train to 5m...")
    train_5m = resample_to_5m(train_1m)

    print("Resampling test to 5m...")
    test_5m = resample_to_5m(test_1m)

    print("Saving files...")
    train_1m.to_csv(TRAIN_1M_FILE, index=False)
    test_1m.to_csv(TEST_1M_FILE, index=False)
    train_5m.to_csv(TRAIN_5M_FILE, index=False)
    test_5m.to_csv(TEST_5M_FILE, index=False)

    print_summary(df, train_1m, test_1m, train_5m, test_5m)
    print("\nDone.")


def sharpe_ratio(returns, timeframe="1m"):
    if len(returns) < 2 or returns.std() == 0:
        return float("nan")
    return float(returns.mean() / returns.std())

def init_experiment_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["label", "N", "H", "T", "sharpe", "signals", "runtime"])

def log_experiment(label, N, H, T, sharpe, signals, runtime):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([label, N, H, T, sharpe, signals, runtime])

    

if __name__ == "__main__":
    main()