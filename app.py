import os
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from services.openweather import search_locations, fetch_location_data
from services.insights import build_insights, answer_with_gemini
from database.db import init_db, save_snapshot, get_history
from models.anomaly_detection import detect_current_anomaly

load_dotenv()
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
init_db()

@app.get('/')
def home():
    return render_template('index.html')

@app.get('/api/search')
def search():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify({'error': 'Enter at least two characters.'}), 400
    try:
        return jsonify(search_locations(query))
    except Exception as exc:
        return jsonify({'error': str(exc)}), 502

@app.get('/api/location')
def location():
    try:
        lat = float(request.args['lat']); lon = float(request.args['lon'])
        name = request.args.get('name', 'Selected location')
        payload = fetch_location_data(lat, lon)
        payload['location'] = name
        payload['insights'] = build_insights(payload)
        payload['ml_anomaly'] = detect_current_anomaly(payload)
        save_snapshot(name, lat, lon, payload)
        return jsonify(payload)
    except KeyError:
        return jsonify({'error': 'Latitude and longitude are required.'}), 400
    except Exception as exc:
        return jsonify({'error': str(exc)}), 502

@app.get('/api/history')
def history():
    return jsonify(get_history())

@app.post('/api/assistant')
def assistant():
    body = request.get_json(silent=True) or {}
    question = (body.get('question') or '').strip()
    data = body.get('data') or {}
    if not question:
        return jsonify({'error': 'Please enter a question.'}), 400
    try:
        answer = answer_with_gemini(question, data)
        return jsonify({'answer': answer})
    except Exception as exc:
        return jsonify({'error': str(exc)}), 502

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
