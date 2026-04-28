import streamlit as st
import requests
import pandas as pd

# --- CONFIG ---
st.set_page_config(page_title="Village Weather Finder", page_icon="🌦️", layout="centered")

# --- LOCAL DATABASE ---
PINCODE_DB = {
    "505301": {"lat": 18.7565, "lon": 79.4448, "name": "Ramagundam / Peddapalli"},
    "505302": {"lat": 18.5000, "lon": 78.9333, "name": "Vemulawada, Rajanna Sircilla"}
}

def get_coords_from_pincode(pin):
    """Fallback: Fetch coordinates for any pincode in India."""
    url = f"https://openstreetmap.org{pin}&country=India&format=json"
    headers = {'User-Agent': 'WeatherAppDemo/1.0'}
    try:
        response = requests.get(url, headers=headers).json()
        if response:
            return {
                "lat": float(response[0]['lat']),
                "lon": float(response[0]['lon']),
                "name": response[0]['display_name'].split(',')[0]
            }
    except:
        return None
    return None

def get_weather(lat, lon):
    """Fetch current weather from Open-Meteo."""
    url = f"https://open-meteo.com{lat}&longitude={lon}&current_weather=true"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

# --- UI ---
st.title("🌦️ Village Weather Dashboard")
st.info("Directly updated for **Vemulawada (505302)**.")

pincode = st.text_input("Enter Indian Pincode", value="505302", max_chars=6)

if st.button("Search Weather"):
    # 1. Check local DB first, then fallback to API lookup
    location = PINCODE_DB.get(pincode) or get_coords_from_pincode(pincode)
    
    if location:
        data = get_weather(location['lat'], location['lon'])
        
        if data:
            current = data['current_weather']
            st.success(f"📍 Found: **{location['name']}**")
            
            # Display Metrics
            m1, m2 = st.columns(2)
            m1.metric("Temperature", f"{current['temperature']}°C")
            m2.metric("Wind Speed", f"{current['windspeed']} km/h")
            
            # Map View
            st.subheader("Location View")
            st.map(pd.DataFrame({'lat': [location['lat']], 'lon': [location['lon']]}))
        else:
            st.error("Weather data currently unavailable.")
    else:
        st.error("Pincode not found. Please check the number.")

st.divider()
st.caption("Using [Open-Meteo](https://open-meteo.com) for weather and [OpenStreetMap](https://www.openstreetmap.org/) for locations.")
