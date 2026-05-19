# EV Charging Optimization Interface

This folder contains a Streamlit interface for configuring the user behavior inputs of `scenario_c_user_behavior.gms` and running the GAMS optimization.

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

3. Open the displayed URL, usually:
   ```text
   http://localhost:8501
   ```

## Features

- Select the EV model. Currently only `TOGG T10F Long Range` is enabled.
- Select the charging station type. Currently only `Ev tipi 220V priz - 2.3 kW` is enabled.
- Enter home-work one-way distance in kilometers.
- Select working days.
- Select home departure and home return hours.
- Update `scenario_c_user_behavior.gms` with daily EV energy demand and home/away profile.
- Run GAMS directly from the interface.

## Files

- `app.py`: Main Streamlit application
- `requirements.txt`: Python dependencies

## Requirements

- Python 3.8+
- Streamlit
- Pandas
- GAMS
- Access to the main project files

The interface does not modify the source files inside `Veri setleri/`. It reads vehicle specs from that folder and writes the selected behavior into the root `scenario_c_user_behavior.gms` model.
