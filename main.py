import os
from flask import Flask, request, jsonify
from db import get_db, insert_reading, fetch_latest_readings
from datetime import datetime
from flask import render_template, send_from_directory
import csv
import os

app = Flask(__name__)
app.static_folder = 'static'
app.template_folder = 'templates'

@app.route('/api/v1/sensor', methods=['POST'])
def ingest_sensor():
    """Expect JSON payload:
    {
      "device_id": "esp01",
      "ldr": 123,
      "water": 0,
      "buzzer": 1,
      "ts": "2025-10-21T12:34:56Z"  # optional ISO timestamp
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    device_id = data.get('device_id') or data.get('id')
    ldr = data.get('ldr')
    water = data.get('water')
    buzzer = data.get('buzzer')
    ts = data.get('ts')

    if not device_id:
        return jsonify({"error": "device_id is required"}), 400

    try:
        if ts:
            ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        else:
            ts = datetime.utcnow()
    except Exception:
        ts = datetime.utcnow()

    try:
        conn = get_db()
        insert_reading(conn, device_id, ldr, water, buzzer, ts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok"}), 201

@app.route('/api/v1/sensor/latest', methods=['GET'])
def latest():
    device_id = request.args.get('device_id')
    limit = int(request.args.get('limit') or 10)
    try:
        conn = get_db()
        rows = fetch_latest_readings(conn, device_id=device_id, limit=limit)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/csv', methods=['GET'])
def csv_data():
    """Read local sensorWater.csv (semicolon-separated) and return JSON.
    Optional query params: status, limit
    """
    csv_path = os.path.join(os.path.dirname(__file__), 'sensorWater.csv')
    status_filter = request.args.get('status')
    limit = int(request.args.get('limit') or 1000)
    if not os.path.exists(csv_path):
        return jsonify({'error': 'CSV not found'}), 404

    rows = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for r in reader:
            # normalize/convert types
            try:
                r['Time(s)'] = int(r.get('Time(s)', '') or 0)
            except Exception:
                r['Time(s)'] = None
            try:
                r['WaterLevel'] = int(r.get('WaterLevel', '') or 0)
            except Exception:
                r['WaterLevel'] = None
            # keep other fields as-is
            rows.append(r)
            if len(rows) >= limit:
                break

    if status_filter:
        rows = [r for r in rows if r.get('Status') == status_filter]

    return jsonify(rows)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
