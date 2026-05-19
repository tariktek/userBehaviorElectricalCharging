import csv

filepath = 'merged_energy_2025.csv'
value_cols = ['solar', 'wind', 'home_consumption']

total = 0
missing = {c: 0 for c in value_cols}
negative = {c: [] for c in value_cols}   # store row indices
flag999  = {c: 0 for c in value_cols}
non_num  = {c: 0 for c in value_cols}
stats    = {c: {'min': float('inf'), 'max': float('-inf'), 'sum': 0.0, 'count': 0} for c in value_cols}

with open(filepath, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        total += 1
        for c in value_cols:
            val = row[c].strip()
            if val == '':
                missing[c] += 1
                continue
            try:
                v = float(val)
                if v == -999:
                    flag999[c] += 1
                elif v < 0:
                    negative[c].append(f"  Row {total}: YEAR={row['YEAR']} MO={row['MO']} DY={row['DY']} HR={row['HR']} val={v}")
                s = stats[c]
                if v < s['min']:
                    s['min'] = v
                if v > s['max']:
                    s['max'] = v
                s['sum'] += v
                s['count'] += 1
            except ValueError:
                non_num[c] += 1

print("=" * 45)
print("       DATA QUALITY REPORT")
print("=" * 45)
print(f"Total rows : {total}")
print()
for c in value_cols:
    s = stats[c]
    count = s['count']
    avg = round(s['sum'] / count, 4) if count > 0 else 'N/A'
    mn  = round(s['min'], 4) if count > 0 else 'N/A'
    mx  = round(s['max'], 4) if count > 0 else 'N/A'
    print(f"--- {c} ---")
    print(f"  Missing (empty) : {missing[c]}")
    print(f"  -999 flag       : {flag999[c]}")
    print(f"  Negative values : {len(negative[c])}")
    print(f"  Non-numeric     : {non_num[c]}")
    print(f"  Min             : {mn}")
    print(f"  Max             : {mx}")
    print(f"  Avg             : {avg}")
    print(f"  Valid rows      : {count}/{total}")
    if negative[c]:
        print("  Negative detail:")
        for line in negative[c][:10]:
            print(line)
    print()

print("=" * 45)
print("SUMMARY:")
all_ok = True
for c in value_cols:
    issues = missing[c] + flag999[c] + len(negative[c]) + non_num[c]
    status = "OK" if issues == 0 else f"ISSUES ({issues})"
    print(f"  {c}: {status}")
    if issues > 0:
        all_ok = False
if all_ok:
    print("  => No issues found!")
print("=" * 45)
