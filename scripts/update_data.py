#!/usr/bin/env python3
"""
Pull season-to-date MLB leaders from FanGraphs and overwrite the two CSVs used by
your app: `batters_2025_2025.csv` and `pitchers_2025_2025.csv`.

- Uses FanGraphs CSV export (adds `csv=1`) with a friendly User-Agent
- Filters out "2 Tms/3 Tms"
- Selects/renames only the columns your app uses
- Preserves your `Salary (Per Season)` by merging from the existing CSVs
- Writes in the same schema/order your app expects
"""
from __future__ import annotations
import os
import sys
import time
from io import BytesIO
from datetime import date
import pandas as pd
import requests

BATTERS_URL  = (
    "https://www.fangraphs.com/leaders/major-league"
    "?pageitems=2000000000&startdate=2025-03-27&enddate={end}"
    "&season=2025&season1=2025&ind=0&team=0&pos=all&type=8&stats=bat&qual=1&month=1000"
)
PITCHERS_URL = (
    "https://www.fangraphs.com/leaders/major-league"
    "?pageitems=2000000000&startdate=2025-03-27&enddate={end}"
    "&season=2025&season1=2025&ind=0&team=0&pos=all&type=8&stats=pit&qual=1&month=1000"
)

HEADERS = {"User-Agent": "mlb-value-tool (github.com/Martin9803/mlb-value-tool)"}
BATTERS_OUT  = "batters_2025_2025.csv"
PITCHERS_OUT = "pitchers_2025_2025.csv"

# Columns your app expects, in order
BATTERS_ORDER = [
    "#", "Name", "Team", "Type", "PA", "G", "WAR", "SLG", "OBP", "HR",
    "RBI", "SB", "R", "BB%", "K%", "AVG", "Salary (Per Season)"
]
PITCHERS_ORDER = [
    "#", "Name", "Team", "Type", "W", "L", "SV", "G", "IP", "K/9", "BB/9",
    "HR/9", "ERA", "FIP", "WAR", "Salary (Per Season)"
]


def _today_str() -> str:
    return os.getenv("END_DATE", date.today().strftime("%Y-%m-%d"))


def fetch_fg_csv(url: str, retries: int = 3, backoff: float = 1.5) -> pd.DataFrame:
    """Fetch a FanGraphs CSV into a DataFrame with simple retry/backoff."""
    if "csv=1" not in url:
        url = f"{url}&csv=1"
    last_exc = None
    for i in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=60)
            resp.raise_for_status()
            return pd.read_csv(BytesIO(resp.content))
        except Exception as exc:  # noqa: BLE001 - log & retry
            last_exc = exc
            time.sleep(backoff ** (i + 1))
    raise RuntimeError(f"Failed to fetch FanGraphs CSV: {last_exc}")


def merge_salary(df: pd.DataFrame, existing_path: str) -> pd.DataFrame:
    """Preserve Salary (Per Season) by merging from existing CSV if present."""
    if os.path.exists(existing_path):
        existing = pd.read_csv(existing_path, encoding="ISO-8859-1")
        if "Salary (Per Season)" in existing.columns:
            sal = existing[["Name", "Team", "Salary (Per Season)"]].copy()
            sal["Name"] = sal["Name"].astype(str).str.strip()
            sal["Team"] = sal["Team"].astype(str).str.strip()
            df["Name"] = df["Name"].astype(str).str.strip()
            df["Team"] = df["Team"].astype(str).str.strip()
            df = df.merge(sal, on=["Name", "Team"], how="left")
            return df
    df["Salary (Per Season)"] = pd.NA
    return df


def normalize_batters(df: pd.DataFrame) -> pd.DataFrame:
    # Drop multi-team summary rows
    df = df[df["Team"].isin(["2 Tms", "3 Tms"]) == False].copy()
    # Map/keep only the columns we need
    keep = {
        "Name": "Name",
        "Team": "Team",
        "G": "G",
        "PA": "PA",
        "WAR": "WAR",
        "SLG": "SLG",
        "OBP": "OBP",
        "HR": "HR",
        "RBI": "RBI",
        "SB": "SB",
        "R": "R",
        "BB%": "BB%",
        "K%": "K%",
        "AVG": "AVG",
    }
    out = pd.DataFrame({new: df.get(old) for old, new in keep.items()})
    out.insert(0, "#", range(1, len(out) + 1))
    out.insert(3, "Type", "Batter")
    return out


def normalize_pitchers(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["Team"].isin(["2 Tms", "3 Tms"]) == False].copy()
    keep = {
        "Name": "Name",
        "Team": "Team",
        "W": "W",
        "L": "L",
        "SV": "SV",
        "G": "G",
        "IP": "IP",
        "K/9": "K/9",
        "BB/9": "BB/9",
        "HR/9": "HR/9",
        "ERA": "ERA",
        "FIP": "FIP",
        "WAR": "WAR",
    }
    out = pd.DataFrame({new: df.get(old) for old, new in keep.items()})
    out.insert(0, "#", range(1, len(out) + 1))
    out.insert(3, "Type", "Pitcher")
    return out


def write_ordered(df: pd.DataFrame, order: list[str], path: str) -> None:
    # Ensure all columns exist; missing -> NA
    for col in order:
        if col not in df.columns:
            df[col] = pd.NA
    df = df[order]
    # Remove legacy index columns if ever present
    for c in list(df.columns):
        if c.lower().startswith("unnamed:"):
            del df[c]
    df.to_csv(path, index=False)


def main() -> int:
    end = _today_str()
    print(f"Fetching FanGraphs leaders through {end}…", flush=True)

    bat_raw = fetch_fg_csv(BATTERS_URL.format(end=end))
    pit_raw = fetch_fg_csv(PITCHERS_URL.format(end=end))

    bat = normalize_batters(bat_raw)
    pit = normalize_pitchers(pit_raw)

    bat = merge_salary(bat, BATTERS_OUT)
    pit = merge_salary(pit, PITCHERS_OUT)

    # Final ordering & write
    write_ordered(bat, BATTERS_ORDER, BATTERS_OUT)
    write_ordered(pit, PITCHERS_ORDER, PITCHERS_OUT)

    print(f"Saved {BATTERS_OUT}: {len(bat)} rows")
    print(f"Saved {PITCHERS_OUT}: {len(pit)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
