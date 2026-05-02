import streamlit as st
import requests
import pandas as pd

# --- CONFIG ---
st.set_page_config(page_title="Farmer Weather Analytics", page_icon="🌾", layout="centered")

st.title("🌾 Farmer Analytics Dashboard")

# --- PINCODE DB ---
PINCODE_DB = {
    "505302": {"lat": 18.5, "lon": 78.9333, "name": "Vemulawada"},
    "505301": {"lat": 18.7565, "lon": 79.4448, "name": "Ramagundam"},
    "524221": {"lat": 14.9565, "lon": 79.5169, "name": "Chakalakonda, Nellore"}    
}

# --- FUNCTIONS ---
def get_historical_weather(lat, lon, start, end):
    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        return res.json()
    except:
        return None


def crop_advisory(avg_rain, avg_temp):
    if avg_rain > 8:
        return "🌾 Suitable for Rice"
    elif avg_rain > 3:
        return "🌽 Suitable for Maize / Cotton"
    else:
        return "🌿 Suitable for Millets / Groundnut"


def risk_alert(total_rain):
    if total_rain < 20:
        return "⚠️ Low rainfall (Drought Risk)"
    elif total_rain > 200:
        return "⚠️ Heavy rainfall (Flood Risk)"
    else:
        return "✅ Normal conditions"


# --- UI INPUT ---
pincode = st.text_input("Enter Pincode", "505302")

col1, col2 = st.columns(2)
start_date = col1.date_input("Start Date")
end_date = col2.date_input("End Date")

# --- ACTION ---
if st.button("Analyze"):
    location = PINCODE_DB.get(pincode)

    if not location:
        st.error("Pincode not found")
    else:
        data = get_historical_weather(
            location['lat'],
            location['lon'],
            str(start_date),
            str(end_date)
        )

        if data and "daily" in data:
            df = pd.DataFrame(data["daily"])

            st.success(f"📍 {location['name']}")

            # --- METRICS ---
            total_rain = df["precipitation_sum"].sum()
            avg_rain = df["precipitation_sum"].mean()
            avg_temp = df["temperature_2m_max"].mean()

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Rainfall (mm)", round(total_rain, 2))
            m2.metric("Avg Rain/day", round(avg_rain, 2))
            m3.metric("Avg Temp (°C)", round(avg_temp, 2))

            st.divider()

            # --- CHART ---
            st.subheader("📈 Weather Trends")

            st.subheader("📈 Precipitation")
            df_chart = df.set_index("time")
            st.line_chart(df_chart[[ "precipitation_sum"]])

            st.subheader("📈 Temparature")
            df_chart = df.set_index("time")
            st.line_chart(df_chart[[ "temperature_2m_max"]])

            # --- ADVISORY ---
            st.subheader("🌱 Crop Advisory")
            st.info(crop_advisory(avg_rain, avg_temp))

            # --- RISK ---
            st.subheader("⚠️ Risk Analysis")
            st.warning(risk_alert(avg_rain))

            # --- DATA TABLE ---
            with st.expander("View Raw Data"):
                st.dataframe(df)

        else:
            st.error("Failed to fetch data")