"""Educational anomaly detection over previously saved pollutant/weather snapshots."""
import numpy as np
from sklearn.ensemble import IsolationForest
from database.db import get_training_rows

FEATURES = ('pm25', 'pm10', 'temperature', 'humidity')

def detect_current_anomaly(payload):
    rows = get_training_rows(limit=100)
    usable = [r for r in rows if all(r.get(k) is not None for k in FEATURES)]
    current = payload.get('pollutants', {}) | payload.get('weather', {})
    current_row = [current.get('pm25'), current.get('pm10'), current.get('temperature'), current.get('humidity')]
    if len(usable) < 15 or any(v is None for v in current_row):
        return {'status': 'Collecting baseline', 'detail': f'{len(usable)}/15 usable saved observations. More observations are needed before anomaly detection.'}
    X = np.asarray([[float(r[k]) for k in FEATURES] for r in usable], dtype=float)
    model = IsolationForest(contamination=0.10, random_state=42)
    model.fit(X)
    prediction = int(model.predict(np.asarray(current_row, dtype=float).reshape(1, -1))[0])
    if prediction == -1:
        return {'status': 'Unusual pattern detected', 'detail': 'The current pollutant/weather combination differs from this project’s saved baseline. This is a statistical flag, not proof of a pollution event.'}
    return {'status': 'Within saved baseline', 'detail': 'The current pollutant/weather combination is within the pattern learned from saved observations.'}
