"""
Sustainable Energy — Wind technical assignment
Combined Wind & Solar Analysis at Altamont Pass (2020)
"""

import io
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from dotenv import load_dotenv 

# =====================================================================
# CREDENTIALS (Sourced from https://developer.nlr.gov/)
#
# If downloading the code, please create a .env file in the same directory with the following content:
#   NLR_API_KEY=YOUR_API_KEY_HERE
#   NLR_EMAIL=YOUR_EMAIL_HERE
# =====================================================================
# Load the variables from the .env file
load_dotenv()

# Fetch the credentials from the environment
API_KEY = os.getenv("NLR_API_KEY")
EMAIL = os.getenv("NLR_EMAIL")

# Check if they loaded correctly
if not API_KEY or not EMAIL:
    print("ERROR: Could not find API_KEY or EMAIL. Did you create the .env file?")
    exit(1)

# =====================================================================
# 1. SeaTitan Power Curve
# =====================================================================
def seatitan_power(v):
    """Approximate power output (kW) of a 10 MW SeaTitan for wind speed v (m/s)."""
    v_in, v_rated, v_out = 4.0, 11.5, 30.0
    P_rated = 10000.0  # kW
    v = np.asarray(v, dtype=float)
    power = np.zeros_like(v)
    
    # Cubic ramp between cut-in and rated
    mask_ramp = (v >= v_in) & (v <= v_rated)
    power[mask_ramp] = P_rated * ((v[mask_ramp] - v_in) / (v_rated - v_in)) ** 3
    
    # Rated power plateau
    mask_rated = (v > v_rated) & (v <= v_out)
    power[mask_rated] = P_rated
    
    return power

# =====================================================================
# 2-4. Fetch NLR Wind Data & Convert
# =====================================================================
def get_wind_data(api_key, email):
    print("Fetching Wind Data from NLR WIND Toolkit...")
    
    # WTK-LED CONUS endpoint
    url = "https://developer.nlr.gov/api/wind-toolkit/v2/wind/wtk-led-conus-download.csv"
    
    params = {
        "api_key": api_key,
        "wkt": "POINT(-121.6583 37.7458)",
        "attributes": "windspeed_100m",
        "names": "2020",
        "email": email,
        "utc": "true",
        "interval": "60",
        "leap_day": "true",
        "csv_format": "true",
    }
    
    response = requests.get(url, params=params, timeout=120)
    
    # --- DIAGNOSTIC STEP ---
    if response.status_code != 200:
        print(f"API Error {response.status_code}: {response.text[:500]}")
        response.raise_for_status()
    # -------------------------

    # Dynamically find the header row (in case the metadata rows change)
    lines = response.text.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if "Year" in line or "Month" in line or "windspeed" in line.lower():
            header_idx = i
            break
            
    if header_idx is None:
        print("ERROR: Could not find a valid CSV header in the response.")
        print("RAW PREVIEW:", response.text[:500])
        return None

    df = pd.read_csv(io.StringIO(response.text), skiprows=header_idx)
    
    # Create datetime index
    df["time"] = pd.to_datetime(df[["Year", "Month", "Day", "Hour", "Minute"]])
    
    # Find the wind speed column dynamically
    wind_col = [c for c in df.columns if "windspeed" in c.lower() or "wind speed" in c.lower()][0]
    df = df[["time", wind_col]].rename(columns={wind_col: "wind_speed_100m"})
    
    # Height correction (100m to 125m)
    alpha = 0.10
    df["wind_speed_125m"] = df["wind_speed_100m"] * (125.0 / 100.0) ** alpha
    
    # Convert to power
    df["power_kw"] = seatitan_power(df["wind_speed_125m"].values)
    
    print(f"  -> Downloaded {len(df)} wind records.")
    return df

# =====================================================================
# 5 & 7. Heat Map Plotting Function
# =====================================================================
def plot_heatmap(df, title, cbar_label, cmap, fname):
    df = df.copy()
    df["hour"] = df["time"].dt.hour
    df["day_of_year"] = df["time"].dt.dayofyear
    
    heat = df.pivot_table(index="hour", columns="day_of_year", 
                          values="power_kw", aggfunc="mean")
    
    fig, ax = plt.subplots(figsize=(16, 5))
    sns.heatmap(heat, cmap=cmap, cbar_kws={"label": cbar_label},
                ax=ax, yticklabels=range(0, 24, 2))
    
    ax.set_xlabel("Day of year (2020)")
    ax.set_ylabel("Hour of day")
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"  -> Saved heat map to {fname}")

# =====================================================================
# 6. Fetch NLR PVWatts Solar Data
# =====================================================================
def get_solar_data(api_key):
    print("Fetching Solar Data from NLR PVWatts...")
    url = "https://developer.nlr.gov/api/pvwatts/v8.json"
    
    params = {
        "api_key": api_key,
        "lat": 37.7458,
        "lon": -121.6583,
        "system_capacity": 10000,
        "module_type": 0,
        "array_type": 0,
        "tilt": 37,
        "azimuth": 180,
        "losses": 14,
        "timeframe": "hourly",
    }
    
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    
    ac_w = response.json()["outputs"]["ac"]
    
    timestamps = pd.date_range("2020-01-01", "2020-12-31 23:00", freq="h")
    # PVWatts ignores leap days, so we drop Feb 29 to align the arrays
    timestamps = timestamps[~((timestamps.month == 2) & (timestamps.day == 29))]
    
    df = pd.DataFrame({
        "time": timestamps,
        "power_kw": np.array(ac_w, dtype=float) / 1000.0
    })
    
    print(f"  -> Downloaded {len(df)} solar records.")
    return df

# =====================================================================
# Main Execution
# =====================================================================
if __name__ == "__main__":
    if API_KEY == "YOUR_API_KEY_HERE" or EMAIL == "your_email@example.com":
        print("ERROR: Please fill in your NLR API key and email at the top of the script.")
        exit(1)

    # 1. Wind
    df_wind = get_wind_data(API_KEY, EMAIL)
    if df_wind is not None:
        plot_heatmap(df_wind, 
                     "Wind Generation — SeaTitan 10 MW, Altamont Pass (125m)",
                     "Wind power (kW)", "viridis", "wind_heatmap.png")
    
    # 2. Solar
    df_solar = get_solar_data(API_KEY)
    if df_solar is not None:
        plot_heatmap(df_solar, 
                     "Solar Generation — 10 MW PV, Altamont Pass",
                     "Solar power (kW)", "YlOrRd", "solar_heatmap.png")
    
    print("\nAnalysis complete! Check the folder for the two PNG images.")