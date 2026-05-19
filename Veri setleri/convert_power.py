import csv
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

DATA_DIR = Path(__file__).resolve().parent
INPUT_FILE  = DATA_DIR / "household_power_consumption.txt"
OUTPUT_FILE = DATA_DIR / "household_power_consumption_hourly_2025.csv"

COL_NAMES = ["Global_active_power"]

print("Reading and aggregating data...")

hourly_data = defaultdict(lambda: defaultdict(list))
skipped = 0
total = 0

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i == 0:
            continue  # skip header row
        line = line.strip()
        if not line:
            continue
        total += 1
        parts = line.split(";")
        if len(parts) != 9:
            skipped += 1
            continue

        date_str, time_str = parts[0], parts[1]
        try:
            dt = datetime.strptime(date_str + " " + time_str, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            skipped += 1
            continue

        # Remap year to 2025, keep month/day/hour
        key = (2025, dt.month, dt.day, dt.hour)

        for j, col in enumerate(COL_NAMES):
            val_str = parts[2 + j]
            if val_str == "?" or val_str == "":
                continue
            try:
                hourly_data[key][col].append(float(val_str))
            except ValueError:
                pass

print(f"Total data lines: {total}, skipped (bad rows): {skipped}")
print(f"Unique hourly buckets with data: {len(hourly_data)}")

# Generate ALL 8760 hours of 2025 (non-leap year)
print("Writing output CSV with all 8760 hours of 2025...")
start = datetime(2025, 1, 1, 0)
all_hours = [(start + timedelta(hours=h)) for h in range(8760)]

missing = 0
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["YEAR", "MO", "DY", "HR", "Global_active_power"])

    for dt in all_hours:
        key = (dt.year, dt.month, dt.day, dt.hour)
        row = [dt.year, dt.month, dt.day, dt.hour]
        bucket = hourly_data.get(key)
        if bucket:
            for col in COL_NAMES:
                vals = bucket[col]
                row.append(round(sum(vals) / len(vals), 5) if vals else "")
        else:
            row += [""] * len(COL_NAMES)
            missing += 1
        writer.writerow(row)

print(f"Hours with data: {8760 - missing}")
print(f"Hours missing (filled with empty): {missing}")
print(f"Total rows written: 8760")
print(f"Done! Output -> {OUTPUT_FILE}")
