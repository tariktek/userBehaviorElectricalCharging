import csv
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path(__file__).resolve().parent
SOLAR_FILE = DATA_DIR / "SOLAR-POWER_Point_Hourly_20250101_20251231_041d03N_028d89E_UTC.csv"
WIND_FILE  = DATA_DIR / "WIND-POWER_Point_Hourly_20250101_20251231_041d03N_028d89E_UTC (1).csv"
HOME_FILE  = DATA_DIR / "household_power_consumption_hourly_2025.csv"
OUTPUT     = DATA_DIR / "merged_energy_2025.csv"

def load_csv(filepath, value_col, skip_header=True):
    """Load a YEAR,MO,DY,HR,value CSV into a dict keyed by (year,mo,dy,hr)."""
    data = {}
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                key = (int(row["YEAR"]), int(row["MO"]), int(row["DY"]), int(row["HR"]))
                val = row[value_col]
                data[key] = val if val != "" else ""
            except (KeyError, ValueError):
                continue
    return data

print("Loading solar data...")
solar = load_csv(SOLAR_FILE, "ALLSKY_SFC_SW_DWN")

print("Loading wind data...")
wind = load_csv(WIND_FILE, "WS10M")

print("Loading home consumption data...")
home = load_csv(HOME_FILE, "Global_active_power")

# Generate all 8760 hours of 2025
start = datetime(2025, 1, 1, 0)
all_hours = [(start + timedelta(hours=h)) for h in range(8760)]

print("Writing merged CSV...")
with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["YEAR", "MO", "DY", "HR", "solar", "wind", "home_consumption"])

    for dt in all_hours:
        key = (dt.year, dt.month, dt.day, dt.hour)
        row = [
            dt.year, dt.month, dt.day, dt.hour,
            solar.get(key, ""),
            wind.get(key, ""),
            home.get(key, ""),
        ]
        writer.writerow(row)

print(f"Done! {len(all_hours)} rows written -> {OUTPUT}")
