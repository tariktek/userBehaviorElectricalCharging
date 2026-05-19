import re
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="EV Charging Optimization", page_icon="EV", layout="wide")

if "has_run_optimization" not in st.session_state:
    st.session_state.has_run_optimization = False

project_root = Path(__file__).resolve().parents[1]
data_dir = project_root / "Veri setleri"
vehicle_specs_csv = data_dir / "vehicle_specs.csv"
common_model = data_dir / "scenario_common_24.gms"
scenario_a_model = project_root / "scenario_a_full_grid.gms"
scenario_b_model = project_root / "scenario_b_hybrid_grid.gms"
gams_model = project_root / "scenario_c_user_behavior.gms"
results_summary = project_root / "results_summary.txt"
gams_path = r"D:\GAMS\53\gams.exe"

DAY_OPTIONS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
STATION_OPTIONS = ["Ev tipi 220V priz - 2.3 kW"]


@st.cache_data
def load_vehicle_specs() -> pd.DataFrame:
    return pd.read_csv(vehicle_specs_csv)


def update_scalar(source: str, name: str, value: float) -> str:
    pattern = rf"({re.escape(name)}(?:\s+'[^']*')?\s*/\s*)[-+]?\d+(?:\.\d+)?(\s*/)"
    replacement = rf"\g<1>{value:.4f}\g<2>"
    updated, count = re.subn(pattern, replacement, source)
    if count != 1:
        raise ValueError(f"{name} parametresi GAMS dosyasında bulunamadı.")
    return updated


def update_home_profile(source: str, leave_hour: int, return_hour: int, has_workday: bool) -> str:
    def replace_home(match: re.Match) -> str:
        hour = int(match.group(1)) - 1
        at_home = 1
        if has_workday and leave_hour <= hour < return_hour:
            at_home = 0
        return f"home('{match.group(1)}') = {at_home}"

    updated, count = re.subn(r"home\('(\d+)'\)\s*=\s*[01]", replace_home, source)
    if count != 24:
        raise ValueError(f"24 adet home(t) ataması bekleniyordu, {count} adet bulundu.")
    return updated


def configure_gams_model(daily_need: float, charger_kw: float, battery_kwh: float, leave_hour: int, return_hour: int, has_workday: bool) -> None:
    source = gams_model.read_text(encoding="utf-8")
    source = update_scalar(source, "daily_ev_need", daily_need)
    source = update_scalar(source, "ev_charge_max", charger_kw)
    source = update_scalar(source, "SoE_max", battery_kwh)
    source = update_home_profile(source, leave_hour, return_hour, has_workday)
    gams_model.write_text(source, encoding="utf-8")


def configure_common_model(daily_need: float, charger_kw: float) -> None:
    source = common_model.read_text(encoding="utf-8")
    source = update_scalar(source, "daily_ev_need", daily_need)
    source = update_scalar(source, "ev_charge_max", charger_kw)
    common_model.write_text(source, encoding="utf-8")


def parse_objective_from_lst(model_path: Path) -> float | None:
    lst_path = model_path.with_suffix(".lst")
    if not lst_path.exists():
        return None
    match = re.search(r"OBJECTIVE VALUE\s+([0-9.]+)", lst_path.read_text(encoding="utf-8", errors="ignore"))
    return float(match.group(1)) if match else None


def parse_existing_cost(label: str, fallback: float) -> float:
    if not results_summary.exists():
        return fallback

    text = results_summary.read_text(encoding="utf-8", errors="ignore")
    return parse_cost_from_text(text, label, fallback)


def parse_cost_from_text(text: str, label: str, fallback: float) -> float:
    pattern = rf"{re.escape(label)}[\s\S]*?- Total cost:\s*([0-9.]+)\s*TL"
    match = re.search(pattern, text)
    return float(match.group(1)) if match else fallback


def write_results_summary(
    cost_a: float,
    cost_b: float,
    cost_c: float,
    selected_vehicle: str,
    selected_station: str,
    daily_km: float,
    daily_need: float,
    workdays: list[str],
    leave_hour: int,
    return_hour: int,
) -> None:
    summary = f"""EV Charging Optimization - Results Summary
=========================================

Scenario A: Full Grid
---------------------
- Model file: scenario_a_full_grid.gms
- Description: Only grid energy is used. EV charging can be scheduled within the 2.3 kW home charger limit.
- Model type: LP
- Status: Optimal
- Total cost: {cost_a:.4f} TL

Scenario B: Hybrid Grid
-----------------------
- Model file: scenario_b_hybrid_grid.gms
- Description: Grid, solar PV, and wind are optimized together. User home/away behavior and solar battery are not included.
- Model type: LP
- Status: Optimal
- Total cost: {cost_b:.4f} TL

Scenario C: User-Behavior Adaptive Hybrid
-----------------------------------------
- Model file: scenario_c_user_behavior.gms
- Description: Final model. Grid, solar PV, wind, solar battery, EV battery state, driving consumption, and home/away behavior are optimized together.
- Model type: MIP
- Status: Optimal
- Total cost: {cost_c:.4f} TL

Current User Inputs
-------------------
- Vehicle: {selected_vehicle}
- Charging station: {selected_station}
- Daily distance: {daily_km:.1f} km
- Daily EV energy need: {daily_need:.4f} kWh
- Workdays: {", ".join(workdays) if workdays else "None"}
- Home departure hour: {leave_hour:02d}:00
- Home return hour: {return_hour:02d}:00

Comparison
----------
- Full Grid -> Hybrid Grid saving: {cost_a - cost_b:.4f} TL
- Hybrid Grid -> User-Behavior Adaptive Hybrid saving: {cost_b - cost_c:.4f} TL
- Full Grid -> User-Behavior Adaptive Hybrid saving: {cost_a - cost_c:.4f} TL

Notes
-----
- Scenario A, B, and C are updated with the same daily EV energy need from the Streamlit interface.
- Scenario C uses binary variables to prevent simultaneous solar battery charge and discharge.
- Scenario C additionally uses home/away behavior and EV battery state constraints.
- Last updated: {datetime.now().strftime("%d.%m.%Y %H:%M")}

How to rerun
------------
1. gams scenario_a_full_grid.gms
2. gams scenario_b_hybrid_grid.gms
3. gams scenario_c_user_behavior.gms
"""
    results_summary.write_text(summary, encoding="utf-8")


def run_gams(model_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [gams_path, str(model_path), "lo=2"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )


vehicles = load_vehicle_specs()
togg = vehicles.iloc[0]
vehicle_name = str(togg["Model"])
battery_kwh = float(togg["Battery_kWh"])
consumption_kwh_100km = float(togg["Est_Consumption_kWh_per_100km"])
home_charger_kw = 2.3

st.title("EV Charging Optimization")
st.markdown("### Kullanıcı davranışına göre Scenario C optimizasyonu")

with st.form("behavior_form"):
    col1, col2 = st.columns(2)

    with col1:
        selected_vehicle = st.selectbox("Araç modeli", [vehicle_name])
        selected_station = st.selectbox("Şarj istasyonu tipi", STATION_OPTIONS)
        one_way_distance = st.number_input(
            "Ev ile iş arası mesafe (km)",
            min_value=0.0,
            max_value=300.0,
            value=20.0,
            step=1.0,
        )

    with col2:
        workdays = st.multiselect("Çalışılan günler", DAY_OPTIONS, default=DAY_OPTIONS[:5])
        leave_hour = st.slider("Evden çıkış saati", min_value=0, max_value=23, value=7, step=1)
        return_hour = st.slider("Eve giriş saati", min_value=1, max_value=24, value=18, step=1)

    submitted = st.form_submit_button("Tüm senaryoları güncelle ve optimizasyonu çalıştır", type="primary")

daily_km = one_way_distance * 2
daily_need = daily_km * consumption_kwh_100km / 100 if workdays else 0.0

st.markdown("---")
metric_cols = st.columns(4)
metric_cols[0].metric("Araç", selected_vehicle)
metric_cols[1].metric("Günlük mesafe", f"{daily_km:.1f} km")
metric_cols[2].metric("Günlük EV ihtiyacı", f"{daily_need:.2f} kWh")
metric_cols[3].metric("Şarj gücü", f"{home_charger_kw:.1f} kW")

if submitted:
    if return_hour <= leave_hour and workdays:
        st.error("Eve giriş saati, evden çıkış saatinden sonra olmalı.")
    elif not all(path.exists() for path in [common_model, scenario_a_model, scenario_b_model, gams_model]):
        st.error("GAMS senaryo dosyalarından biri bulunamadı.")
    else:
        try:
            configure_common_model(
                daily_need=daily_need,
                charger_kw=home_charger_kw,
            )
            configure_gams_model(
                daily_need=daily_need,
                charger_kw=home_charger_kw,
                battery_kwh=battery_kwh,
                leave_hour=int(leave_hour),
                return_hour=int(return_hour),
                has_workday=bool(workdays),
            )
            st.success("Scenario A, B ve C aynı kullanıcı girdilerine göre güncellendi.")

            scenario_models = {
                "Scenario A": scenario_a_model,
                "Scenario B": scenario_b_model,
                "Scenario C": gams_model,
            }
            scenario_results = {}

            with st.spinner("GAMS optimizasyonları çalışıyor..."):
                for scenario_name, model_path in scenario_models.items():
                    result = run_gams(model_path)
                    scenario_results[scenario_name] = result
                    if result.returncode != 0:
                        st.error(f"{scenario_name} çalıştırılırken hata oluştu.")
                        st.code(result.stderr or result.stdout)
                        break

            if all(result.returncode == 0 for result in scenario_results.values()) and len(scenario_results) == 3:
                cost_a = parse_objective_from_lst(scenario_a_model)
                cost_b = parse_objective_from_lst(scenario_b_model)
                cost_c = parse_objective_from_lst(gams_model)

                if cost_a is not None and cost_b is not None and cost_c is not None:
                    st.success("Tüm GAMS optimizasyonları optimal olarak tamamlandı.")
                    write_results_summary(
                        cost_a=cost_a,
                        cost_b=cost_b,
                        cost_c=cost_c,
                        selected_vehicle=selected_vehicle,
                        selected_station=selected_station,
                        daily_km=daily_km,
                        daily_need=daily_need,
                        workdays=workdays,
                        leave_hour=int(leave_hour),
                        return_hour=int(return_hour),
                    )
                    st.session_state.has_run_optimization = True
                else:
                    st.error("Senaryo maliyetlerinden biri .lst dosyasından okunamadı.")
        except Exception as exc:
            st.error(f"İşlem tamamlanamadı: {exc}")

st.markdown("---")
st.header("Senaryo Özeti")
if st.session_state.has_run_optimization:
    try:
        summary_text = results_summary.read_text(encoding="utf-8")
        scenario_costs = pd.DataFrame(
            [
                {
                    "Senaryo": "Scenario A",
                    "Fiyat": f"{parse_cost_from_text(summary_text, 'Scenario A: Full Grid', 157.6198):.4f} TL",
                },
                {
                    "Senaryo": "Scenario B",
                    "Fiyat": f"{parse_cost_from_text(summary_text, 'Scenario B: Hybrid Grid', 51.3304):.4f} TL",
                },
                {
                    "Senaryo": "Scenario C",
                    "Fiyat": f"{parse_cost_from_text(summary_text, 'Scenario C: User-Behavior Adaptive Hybrid', 49.5261):.4f} TL",
                },
            ]
        )
        st.table(scenario_costs)
        with st.expander("Logun tamamını göster"):
            st.text(summary_text)
    except FileNotFoundError:
        st.info("results_summary.txt bulunamadı.")

st.markdown("---")
st.caption("Scenario A, B ve C aynı günlük EV ihtiyacına göre güncellenir; Scenario C ayrıca kullanıcı davranışı kısıtlarını kullanır.")
