import csv
from pathlib import Path
from datetime import datetime, timedelta

# CSV dosyasını oku
data_dir = Path(__file__).resolve().parent
csv_file = data_dir / "merged_energy_2025.csv"
prices_file = data_dir / "energy_prices.csv"
behavior_file = data_dir / "user_behavior.csv"
gams_out = data_dir / "gams_input.gms"

data = []
with open(csv_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

print(f"Yüklenen satır sayısı: {len(data)}")

# GAMS kodunu oluştur - 5 gün (120 saat)
hours = 5 * 24
gams_code = f"""
SETS t Hours / 1*{hours} /;

PARAMETERS
    price_grid(t)
    price_solar(t)
    price_wind(t)
    solar_cap(t)
    wind_cap(t)
    load_house(t)
    home(t);
"""

# Her saat için veri ekle - sadece 7 gün (168 saat)
import csv as _csv

# Read price table (24 hours)
prices = []
with open(prices_file, 'r', encoding='utf-8') as pf:
    pr = _csv.DictReader(pf)
    for row in pr:
        prices.append(row)

# Read user behavior (hours 0-23 from Monday column)
behavior = []
with open(behavior_file, 'r', encoding='utf-8') as bf:
    br = _csv.DictReader(bf)
    for row in br:
        behavior.append(row)

hours_count = min(hours, len(data))
for i, row in enumerate(data[:hours_count], 1):
    try:
        solar = float(row.get('solar', 0) or 0)
        wind = float(row.get('wind', 0) or 0)
        demand = float(row.get('home_consumption', 0) or 0)
    except (ValueError, KeyError):
        solar, wind, demand = 0, 0, 0

    # round to 4 decimals
    gams_code += f"solar_cap('{i}') = {solar:.4f};\n"
    gams_code += f"wind_cap('{i}') = {wind:.4f};\n"
    gams_code += f"load_house('{i}') = {demand:.4f};\n"

    # price index (hour of day)
    hour_of_day = (i-1) % 24
    if prices:
        pg = float(prices[hour_of_day]['Sebeke_TL_per_kWh'])
        ps = float(prices[hour_of_day]['Solar_TL_per_kWh'])
        pw = float(prices[hour_of_day]['Ruzgar_TL_per_kWh'])
    else:
        pg, ps, pw = 2.5, 0.2, 0.5

    gams_code += f"price_grid('{i}') = {pg:.2f};\n"
    gams_code += f"price_solar('{i}') = {ps:.2f};\n"
    gams_code += f"price_wind('{i}') = {pw:.2f};\n"

    # home flag from behavior Monday column if available
    if behavior:
        v = behavior[hour_of_day].get('Pazartesi','').strip()
        home_flag = 1 if v == 'Evde' else 0
    else:
        # default: car at home during night hours
        home_flag = 1 if (hour_of_day < 7 or hour_of_day >= 18) else 0
    gams_code += f"home('{i}') = {home_flag};\n"

# Kalan kod
gams_code += """
VARIABLES x_solar(t), x_wind(t), x_grid(t), total_cost;
POSITIVE VARIABLES x_solar, x_wind, x_grid;

EQUATIONS eq1(t), eq2(t), eq3(t), eq4;
eq1(t).. x_solar(t) + x_wind(t) + x_grid(t) =E= load_house(t);
eq2(t).. x_solar(t) =L= solar_cap(t);
eq3(t).. x_wind(t) =L= wind_cap(t);
eq4.. total_cost =E= SUM(t, 0.5*x_solar(t) + 0.7*x_wind(t) + 5.0*x_grid(t));

MODEL m /ALL/;
SOLVE m MIN total_cost USING LP;
DISPLAY total_cost.l;
"""

# GAMS dosyasını ASCII'de kaydet
with open(gams_out, "w", encoding="ascii") as f:
    f.write(gams_code)

print(f"GAMS modeli oluşturuldu: {gams_out}")
print(f"Toplam satır: {len(data)}")
print(f"İlk 5 satır:")
for i in range(min(5, len(data))):
    print(f"  Saat {i+1}: Solar={data[i]['solar']}, Wind={data[i]['wind']}, Demand={data[i]['home_consumption']}")
