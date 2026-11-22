import os
import requests

BASE = 'https://api.openweathermap.org'
TIMEOUT = 15

def _key():
    key = os.getenv('OPENWEATHER_API_KEY')
    if not key:
        raise RuntimeError('OpenWeatherMap API key is missing. Add it to your .env file.')
    return key

def _get(path, params):
    params['appid'] = _key()
    response = requests.get(f'{BASE}{path}', params=params, timeout=TIMEOUT)
    if response.status_code == 401:
        raise RuntimeError('OpenWeatherMap rejected the API key. Check your key and API access.')
    if response.status_code == 404:
        raise RuntimeError('Location or weather data was not found.')
    response.raise_for_status()
    return response.json()

def search_locations(query):
    rows = _get('/geo/1.0/direct', {'q': query, 'limit': 6})
    return [{'name': r.get('name'), 'state': r.get('state', ''), 'country': r.get('country', ''),
             'lat': r['lat'], 'lon': r['lon'],
             'label': ', '.join(x for x in [r.get('name'), r.get('state'), r.get('country')] if x)} for r in rows]

def fetch_location_data(lat, lon):
    # Both APIs use the exact same coordinates returned by geocoding.
    weather = _get('/data/2.5/weather', {'lat': lat, 'lon': lon, 'units': 'metric'})
    pollution = _get('/data/2.5/air_pollution', {'lat': lat, 'lon': lon})
    forecast = _get('/data/2.5/air_pollution/forecast', {'lat': lat, 'lon': lon})
    if not pollution.get('list'):
        raise RuntimeError('Air-quality data is currently unavailable for this coordinate.')
    current = pollution['list'][0]
    c = current.get('components', {})
    w = weather.get('main', {})
    weather_desc = (weather.get('weather') or [{}])[0].get('description', 'Unavailable')
    forecast_rows = []
    for row in forecast.get('list', [])[:24]:
        fc = row.get('components', {})
        forecast_rows.append({'time': row.get('dt'), 'aqi': int(row.get('main', {}).get('aqi', 0)),
                              'pm25': fc.get('pm2_5'), 'pm10': fc.get('pm10')})
    return {
        'coordinates': {'lat': lat, 'lon': lon},
        'observed_at': current.get('dt'),
        'ow_aqi': int(current.get('main', {}).get('aqi', 0)),
        'aqi_label': {1:'Good', 2:'Fair', 3:'Moderate', 4:'Poor', 5:'Very Poor'}.get(int(current.get('main', {}).get('aqi', 0)), 'Unavailable'),
        'pollutants': {'pm25': c.get('pm2_5'), 'pm10': c.get('pm10'), 'co': c.get('co'), 'no': c.get('no'),
                       'no2': c.get('no2'), 'o3': c.get('o3'), 'so2': c.get('so2'), 'nh3': c.get('nh3')},
        'weather': {'temperature': w.get('temp'), 'feels_like': w.get('feels_like'), 'humidity': w.get('humidity'),
                    'pressure': w.get('pressure'), 'wind_speed': weather.get('wind', {}).get('speed'),
                    'description': weather_desc, 'visibility': weather.get('visibility')},
        'forecast': forecast_rows
    }
