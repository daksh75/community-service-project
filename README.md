# Smart AQI AI

A Flask-based air-quality and weather dashboard. It searches a place through OpenWeatherMap Geocoding, then requests current air pollution and weather using the exact same latitude/longitude. It stores each lookup in SQLite and provides an optional Gemini-powered question-answer assistant.

## Features
- Search cities, districts and localities with geocoding suggestions.
- Fetch current air-pollution components and weather for one shared coordinate pair.
- Show OpenWeather's 1–5 air-quality category and 24-hour air-pollution forecast.
- Save lookup snapshots in SQLite and view search history.
- Ask a Gemini assistant for explanations based on the selected live data.
- Run an Isolation Forest anomaly check after at least 15 usable observations have been saved.
- Responsive dashboard with Chart.js.

## Setup (Windows PowerShell)
1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env` and add your own OpenWeatherMap API key. Add a Gemini API key to enable the AI assistant.
6. Run:
   ```powershell
   python app.py
   ```
7. Open http://127.0.0.1:5000 in your browser.

## API notes
- OpenWeatherMap current weather: `/data/2.5/weather`
- OpenWeatherMap current air pollution: `/data/2.5/air_pollution`
- OpenWeatherMap air pollution forecast: `/data/2.5/air_pollution/forecast`
- OpenWeatherMap direct geocoding: `/geo/1.0/direct`

The dashboard intentionally labels the provider's AQI as **OpenWeather AQI (1–5)**. It is not the Indian CPCB AQI (0–500). Do not compare these scales directly. Current pollutant concentrations are point-in-time API values and should not be presented as official CPCB sub-indices without the required averaging periods and methodology.

## Important before publishing
- Never commit `.env` or expose API keys in frontend JavaScript.
- Regenerate any API key that was previously pasted into public or shared code.
- Check your OpenWeatherMap plan and rate limits.
- This is an educational information tool, not a medical device or official regulatory monitoring station.

## Suggested viva demonstration
1. Search a locality (not just a large city).
2. Select the correct result from geocoding suggestions.
3. Explain that both AQI and weather requests use the same latitude and longitude.
4. Show pollutant values and the hourly air-pollution forecast.
5. Ask the AI assistant to explain the current conditions.
6. Open search history and show the SQLite records.

## Current scope
The current version uses the provider's AQI category and provider forecast. Its Isolation Forest anomaly detector requires at least 15 usable saved observations before producing a baseline-based flag. It does not claim to train a reliable AQI prediction model from a small number of live snapshots. A defensible predictive ML extension should be added after collecting a sufficiently large, timestamped historical dataset and validating it with a time-based train/test split.
