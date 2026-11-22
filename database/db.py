import sqlite3
import json
import os
from datetime import datetime, timezone

# Vercel temporary database location
DB_PATH = '/tmp/smart_aqi.db'


def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with connect() as con:
        con.execute('''CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            aqi_level INTEGER,
            category TEXT,
            temperature REAL,
            humidity REAL,
            pm25 REAL,
            pm10 REAL,
            observed_at INTEGER,
            saved_at TEXT NOT NULL
        )''')


def save_snapshot(name, lat, lon, payload):
    p = payload.get('pollutants', {})
    w = payload.get('weather', {})

    with connect() as con:
        con.execute('''INSERT INTO snapshots
        (location,latitude,longitude,aqi_level,category,temperature,
        humidity,pm25,pm10,observed_at,saved_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (
            name, lat, lon,
            payload.get('ow_aqi'),
            payload.get('aqi_label'),
            w.get('temperature'),
            w.get('humidity'),
            p.get('pm25'),
            p.get('pm10'),
            payload.get('observed_at'),
            datetime.now(timezone.utc).isoformat()
        ))


def get_history(limit=50):
    with connect() as con:
        rows = con.execute(
            'SELECT * FROM snapshots ORDER BY id DESC LIMIT ?',
            (limit,)
        ).fetchall()

        return [dict(r) for r in rows]


def get_training_rows(limit=100):
    with connect() as con:
        rows = con.execute(
            '''SELECT pm25,pm10,temperature,humidity
            FROM snapshots ORDER BY id DESC LIMIT ?''',
            (limit,)
        ).fetchall()

        return [dict(r) for r in rows]