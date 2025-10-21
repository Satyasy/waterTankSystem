# IoT Sensor Backend & Dashboard (Flask + MariaDB + Streamlit)

This project provides a comprehensive IoT monitoring system with Flask backend and advanced Streamlit dashboard for ESP8266 water tank sensors.

## 📁 Project Files

### Backend (Flask API)
- `main.py` - Flask REST API with endpoints to ingest and query sensor data
- `db.py` - Database helper using mysql-connector pooling
- `models.sql` - SQL schema for database and `sensor_readings` table
- `send_test.py` - Python client to POST test data

### Frontend (Streamlit Dashboard)
- `dashboard.py` - **Advanced Streamlit dashboard** with multi-page analytics
- `templates/dashboard.html` - (Legacy) HTML dashboard with Chart.js
- `sensorWater.csv` - Sample sensor data file

### Configuration
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - MariaDB container setup
- `.env.example` - Environment variables template

## 🚀 Quick Start

### Option 1: Run Streamlit Dashboard (Recommended)

1. Install dependencies

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

2. Run the Streamlit dashboard

```powershell
streamlit run dashboard.py
```

3. Open browser at `http://localhost:8501`

**Dashboard Features:**
- 📊 **Overview Dashboard**: Real-time KPIs, water level trends, status distribution
- 📈 **Advanced Analytics**: Statistical analysis, anomaly detection, trend analysis, predictive insights
- 📋 **Data Explorer**: Interactive table with search, filter, sort, and pagination
- ⚙️ **Settings & Export**: Export to CSV/JSON/Excel, configure thresholds, system info
- 🔄 **Auto-refresh**: Optional 30-second auto-refresh
- 🎨 **Interactive Charts**: Plotly charts with zoom, pan, hover tooltips
- 🔍 **Smart Filters**: Status, water level range, light status filters
- 📊 **Multi-source Data**: Supports CSV file and/or database data

### Option 2: Run Flask Backend API

1. Install dependencies (same as above)

2. Prepare MariaDB / MySQL (optional - use Docker)

```powershell
docker-compose up -d
# Then create schema
mysql -h 127.0.0.1 -P 3306 -u root -pexample < models.sql
```

3. Set environment variables

```powershell
$env:DB_HOST='127.0.0.1'
$env:DB_USER='root'
$env:DB_PASS='example'
$env:DB_NAME='iot_sensors'
```

4. Run the Flask API server

```powershell
python main.py
```

5. Test the API

```powershell
# Send test data
python send_test.py

# Query latest readings
curl 'http://127.0.0.1:5000/api/v1/sensor/latest?limit=10'

# Query CSV data
curl 'http://127.0.0.1:5000/api/v1/csv?status=CRITICAL&limit=100'
```

## 📡 API Endpoints

### Flask REST API

- `POST /api/v1/sensor` - Ingest sensor data from ESP8266
  - Payload: `{"device_id": "esp01", "ldr": 450, "water": 1, "buzzer": 0}`
  
- `GET /api/v1/sensor/latest` - Get latest sensor readings from database
  - Query params: `device_id`, `limit`
  
- `GET /api/v1/csv` - Read and filter CSV data
  - Query params: `status`, `limit`
  
- `GET /dashboard` - Legacy HTML dashboard (use Streamlit instead)

## 🔌 ESP8266 Integration

```cpp
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "YOUR_SSID";
const char* pass = "YOUR_PASS";
const char* server = "http://<server-ip>:5000/api/v1/sensor";

void setup(){
  Serial.begin(115200);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) delay(500);
}

void loop(){
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(server);
    http.addHeader("Content-Type", "application/json");
    String payload = "{\"device_id\":\"esp01\",\"ldr\":450,\"water\":1,\"buzzer\":0}";
    int code = http.POST(payload);
    String resp = http.getString();
    http.end();
  }
  delay(60000);
}
```

Notes:
- `mysql-connector-python` provides a pure-Python connector compatible with MariaDB. For production use, consider `PyMySQL`/`mysqlclient` or an ORM like SQLAlchemy.
- The code is intentionally minimal. Next steps could include authentication, input validation, rate limiting, and richer query endpoints.
