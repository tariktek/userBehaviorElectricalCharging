import csv
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

print("=" * 60)
print("EV CHARGING OPTIMIZATION - 3 Scenario Model Creator")
print("=" * 60)

# 1. Read Data
print("\n[1] Reading data files...")

data_dir = Path(__file__).resolve().parent

# Vehicle specifications
vehicle = pd.read_csv(data_dir / "vehicle_specs.csv").iloc[0]
print(f"    OK Vehicle: {vehicle['Model']}")
print(f"    OK Battery: {vehicle['Battery_kWh']} kWh")
print(f"    OK AC Charger: {vehicle['AC_ChargerKW']} kW")

# Prices
prices = pd.read_csv(data_dir / "energy_prices.csv")
print(f"    OK Energy Prices: 24 hours")

# Behavior
behavior = pd.read_csv(data_dir / "user_behavior.csv")
daily_consumption = behavior.iloc[0]['Günlük_tüketim_kWh']
print(f"    OK Daily Consumption: {daily_consumption} kWh")

# Real solar/wind data
merged = pd.read_csv(data_dir / "merged_energy_2025.csv")
print(f"    OK Merged Energy Data: {len(merged)} rows")

# 2. Create Demand Profile
print("\n[2] Creating demand profile...")

# 5 days x 24 hours = 120 hours
demand_profile = []
total_hours = 5 * 24

for day in range(5):
    for hour in range(24):
        if 7 <= hour <= 17:  # 07:00-18:00 driving
            hourly_demand = daily_consumption / 10
        else:
            hourly_demand = 0
        
        demand_profile.append({
            'hour': hour,
            'day': day + 1,
            'global_hour': day * 24 + hour,
            'demand': hourly_demand
        })

print(f"    OK Total hours: {len(demand_profile)}")
print(f"    OK Daily consumption: {daily_consumption:.2f} kWh")
print(f"    OK Hourly consumption (during work): {daily_consumption/10:.3f} kWh")

# 3. Read Solar and Wind Capacities
print("\n[3] Reading solar and wind capacities...")

renewable_data = []
for idx, row in merged.iterrows():
    if idx >= 120:  # First 5 days
        break
    
    solar_val = 0.0 if pd.isna(row['solar']) else float(row['solar'])
    wind_val = 0.0 if pd.isna(row['wind']) else float(row['wind'])
    
    renewable_data.append({
        'hour': idx,
        'solar': solar_val,
        'wind': wind_val
    })

print(f"    OK Solar/Wind data: {len(renewable_data)} hours")
solar_vals = [x['solar'] for x in renewable_data]
wind_vals = [x['wind'] for x in renewable_data]
print(f"    OK Avg Solar: {sum(solar_vals)/len(solar_vals) if len(solar_vals) > 0 else 0:.3f} kWh/hour")
print(f"    OK Avg Wind: {sum(wind_vals)/len(wind_vals) if len(wind_vals) > 0 else 0:.3f} kWh/hour")

# 4. Create GAMS Models
print("\n[4] Creating GAMS models...\n")

# MODEL A: Grid-Only
print("    MODEL A: Grid-Only")
model_a = f"""
SETS t Hours / 1*120 /;

PARAMETERS
   demand(t)     'Saatlik talep (kWh)'
   price_grid(t) 'Şebeke fiyatı (TL/kWh)';

"""

# Talep değerlerini ekle
for d in demand_profile:
    model_a += f"demand('{d['global_hour']+1}') = {d['demand']:.4f};\n"

# Fiyatları ekle (5 gün tekrarlandığından)
for h in range(120):
    price_idx = h % 24
    price = prices.iloc[price_idx]['Sebeke_TL_per_kWh']
    model_a += f"price_grid('{h+1}') = {price};\n"

model_a += """
VARIABLES
   x_grid(t)    'Şebeke enerjisi (kWh)'
   cost_grid    'Toplam şebeke maliyeti (TL)';

POSITIVE VARIABLES x_grid;

EQUATIONS
   demand_eq(t)  'Talep denklemi'
   cost_def      'Maliyet tanımı';

demand_eq(t)..   x_grid(t) =E= demand(t);
cost_def..       cost_grid =E= SUM(t, price_grid(t) * x_grid(t));

MODEL scenario_a /ALL/;
SOLVE scenario_a MIN cost_grid USING LP;

DISPLAY cost_grid.l, x_grid.l;
"""

with open(r"d:\GAMS\53\scenario_a_grid_only.gms", "w", encoding="ascii", errors="replace") as f:
    f.write(model_a)
print("         OK scenario_a_grid_only.gms created")

# MODEL B: Hibrit (Optimal)
print("    MODEL B: Hibrit Optimal (Hybrid Optimal)")
model_b = f"""
SETS t Hours / 1*120 /;

PARAMETERS
   demand(t)      'Saatlik talep (kWh)'
   solar_cap(t)   'Solar kapasite (kWh)'
   wind_cap(t)    'Rüzgar kapasite (kWh)'
   price_grid(t)  'Şebeke fiyatı (TL/kWh)'
   price_solar    'Solar maliyeti (TL/kWh)' / 0.20 /
   price_wind     'Rüzgar maliyeti (TL/kWh)' / 0.50 /;

"""

# Talep değerlerini ekle
for d in demand_profile:
    model_b += f"demand('{d['global_hour']+1}') = {d['demand']:.4f};\n"

# Solar/Rüzgar/Fiyatları ekle
for h in range(120):
    price_idx = h % 24
    price = prices.iloc[price_idx]['Sebeke_TL_per_kWh']
    solar = renewable_data[h]['solar']
    wind = renewable_data[h]['wind']
    
    model_b += f"solar_cap('{h+1}') = {solar:.4f};\n"
    model_b += f"wind_cap('{h+1}') = {wind:.4f};\n"
    model_b += f"price_grid('{h+1}') = {price};\n"

model_b += """
VARIABLES
   x_grid(t)    'Şebeke enerjisi (kWh)'
   x_solar(t)   'Solar enerjisi (kWh)'
   x_wind(t)    'Rüzgar enerjisi (kWh)'
   cost_total   'Toplam maliyet (TL)';

POSITIVE VARIABLES x_grid, x_solar, x_wind;

EQUATIONS
   demand_eq(t)    'Talep denklemi'
   solar_limit(t)  'Solar kapasite sınırı'
   wind_limit(t)   'Rüzgar kapasite sınırı'
   cost_def        'Maliyet tanımı';

demand_eq(t)..    x_solar(t) + x_wind(t) + x_grid(t) =E= demand(t);
solar_limit(t)..  x_solar(t) =L= solar_cap(t);
wind_limit(t)..   x_wind(t) =L= wind_cap(t);
cost_def..        cost_total =E= SUM(t, price_solar*x_solar(t) + price_wind*x_wind(t) + price_grid(t)*x_grid(t));

MODEL scenario_b /ALL/;
SOLVE scenario_b MIN cost_total USING LP;

DISPLAY cost_total.l, x_grid.l, x_solar.l, x_wind.l;
"""

with open(r"d:\GAMS\53\scenario_b_hybrid_optimal.gms", "w", encoding="ascii", errors="replace") as f:
    f.write(model_b)
print("         OK scenario_b_hybrid_optimal.gms created")

# MODEL C: Hibrit + Davranış Adaptif
print("    MODEL C: Hibrit Davranış-Adaptif (Behavior-Adaptive)")
model_c = f"""
SETS t Hours / 1*120 /;

PARAMETERS
   demand(t)      'Saatlik talep (kWh)'
   solar_cap(t)   'Solar kapasite (kWh)'
   wind_cap(t)    'Rüzgar kapasite (kWh)'
   price_grid(t)  'Şebeke fiyatı (TL/kWh)'
   price_solar    'Solar maliyeti (TL/kWh)' / 0.20 /
   price_wind     'Rüzgar maliyeti (TL/kWh)' / 0.50 /
   max_charge(t)  'Maksimum şarj gücü (kW)';

"""

# Talep değerlerini ekle
for d in demand_profile:
    model_c += f"demand('{d['global_hour']+1}') = {d['demand']:.4f};\n"

# Solar/Rüzgar/Fiyat/Max Charge ekle
for h in range(120):
    price_idx = h % 24
    price = prices.iloc[price_idx]['Sebeke_TL_per_kWh']
    solar = renewable_data[h]['solar']
    wind = renewable_data[h]['wind']
    
    # Davranış-adaptif kısıtlar:
    # Gece 23-07: yavaş şarj (≤5 kW AC şarj)
    # Puant 18-23: moderate (≤7 kW)
    # Gündüz 07-18: standart (≤11 kW, ama talep de düşük)
    
    if 23 <= price_idx or price_idx < 7:  # Gece
        max_charge_val = 5.0
    elif 18 <= price_idx <= 22:  # Puant
        max_charge_val = 7.0
    else:  # Gündüz
        max_charge_val = 11.0
    
    model_c += f"solar_cap('{h+1}') = {solar:.4f};\n"
    model_c += f"wind_cap('{h+1}') = {wind:.4f};\n"
    model_c += f"price_grid('{h+1}') = {price};\n"
    model_c += f"max_charge('{h+1}') = {max_charge_val};\n"

model_c += """
VARIABLES
   x_grid(t)    'Şebeke enerjisi (kWh)'
   x_solar(t)   'Solar enerjisi (kWh)'
   x_wind(t)    'Rüzgar enerjisi (kWh)'
   cost_total   'Toplam maliyet (TL)';

POSITIVE VARIABLES x_grid, x_solar, x_wind;

EQUATIONS
   demand_eq(t)      'Talep denklemi'
   solar_limit(t)    'Solar kapasite sınırı'
   wind_limit(t)     'Rüzgar kapasite sınırı'
   charge_limit(t)   'Şarj gücü sınırı'
   cost_def          'Maliyet tanımı';

demand_eq(t)..    x_solar(t) + x_wind(t) + x_grid(t) =E= demand(t);
solar_limit(t)..  x_solar(t) =L= solar_cap(t);
wind_limit(t)..   x_wind(t) =L= wind_cap(t);
charge_limit(t).. x_solar(t) + x_wind(t) + x_grid(t) =L= max_charge(t);
cost_def..        cost_total =E= SUM(t, price_solar*x_solar(t) + price_wind*x_wind(t) + price_grid(t)*x_grid(t));

MODEL scenario_c /ALL/;
SOLVE scenario_c MIN cost_total USING LP;

DISPLAY cost_total.l, x_grid.l, x_solar.l, x_wind.l;
"""

with open(r"d:\GAMS\53\scenario_c_behavior_adaptive.gms", "w", encoding="ascii", errors="replace") as f:
    f.write(model_c)
print("         OK scenario_c_behavior_adaptive.gms created")

print("\n" + "=" * 60)
print("OK! All 3 models created:")
print("   - scenario_a_grid_only.gms")
print("   - scenario_b_hybrid_optimal.gms")
print("   - scenario_c_behavior_adaptive.gms")
print("\n   Run with:")
print("   cd D:\\GAMS\\53")
print("   gams scenario_a_grid_only.gms")
print("   gams scenario_b_hybrid_optimal.gms")
print("   gams scenario_c_behavior_adaptive.gms")
print("=" * 60)
