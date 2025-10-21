# 💡 IoT Dashboard - Cheat Sheet

## 🚀 Quick Commands

```powershell
# Start Dashboard (Quickest)
.\start-dashboard.ps1

# Start Dashboard (Manual)
streamlit run dashboard.py

# Start Flask API
python main.py

# Start Database
docker-compose up -d

# Test API
python send_test.py
```

## 🌐 URLs

- Dashboard: `http://localhost:8501`
- Flask API: `http://localhost:5000`
- Database: `localhost:3306`

## 📊 Dashboard Pages

1. **Overview** - KPIs & main charts
2. **Analytics** - Stats, anomalies, trends, predictions
3. **Explorer** - Data table with search/filter
4. **Settings** - Export & configuration

## 🎛️ Sidebar Controls

- Data Source: CSV / DB / Both
- Status Filter: All, CRITICAL, LOW, MEDIUM, FULL
- Water Level: Slider range
- Light: Night only checkbox
- Auto-refresh: 30s toggle

## 📡 API Endpoints

```bash
# Send sensor data
POST /api/v1/sensor
{"device_id":"esp01","ldr":450,"water":1,"buzzer":0}

# Get latest DB readings
GET /api/v1/sensor/latest?device_id=esp01&limit=10

# Get CSV data with filter
GET /api/v1/csv?status=CRITICAL&limit=100
```

## 🔌 ESP8266 Quick Code

```cpp
#include <ESP8266HTTPClient.h>

const char* server = "http://IP:5000/api/v1/sensor";

void sendData() {
  HTTPClient http;
  http.begin(server);
  http.addHeader("Content-Type", "application/json");
  String payload = "{\"device_id\":\"esp01\",\"ldr\":" 
                   + String(analogRead(A0)) + "}";
  http.POST(payload);
  http.end();
}
```

## 🗄️ Database Quick Setup

```powershell
# Docker way
docker-compose up -d
mysql -h 127.0.0.1 -u root -pexample < models.sql

# Env vars
$env:DB_HOST='127.0.0.1'
$env:DB_USER='root'
$env:DB_PASS='example'
$env:DB_NAME='iot_sensors'
```

## 📥 Export Data

1. Go to Settings & Export
2. Choose format: CSV / JSON / Excel
3. Click Download button
4. Check: "Export only filtered data" if needed

## 🔍 Common Filters

```
Status = CRITICAL          # Show critical alerts only
WaterLevel = 0-100         # Low levels
LightStatus = NIGHT        # Night readings
Device = esp01             # Specific device
Limit = 50                 # Reduce data load
```

## 🎨 Chart Types Available

- Line: Water level trends
- Pie: Status distribution  
- Bar: Buzzer/LED activity
- Scatter: Anomaly detection
- Histogram: Distribution
- Gauge: Health score
- Sunburst: Transitions

## 🔧 Troubleshooting

```powershell
# Port already in use?
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Dependencies not installed?
pip install -r requirements.txt --force-reinstall

# Cache issues?
streamlit cache clear

# DB connection failed?
docker-compose ps
mysql -h 127.0.0.1 -u root -p
```

## 📁 Key Files

- `dashboard.py` - Main Streamlit app
- `main.py` - Flask API server
- `db.py` - Database functions
- `sensorWater.csv` - Data file
- `requirements.txt` - Dependencies
- `start-dashboard.ps1` - Quick start

## 🎯 Feature Quick Access

| Feature | Location |
|---------|----------|
| KPI Metrics | Overview → Top cards |
| Charts | Overview → 4 chart panels |
| Statistics | Analytics → Tab 1 |
| Anomalies | Analytics → Tab 2 |
| Trends | Analytics → Tab 3 |
| Health Score | Analytics → Tab 4 |
| Search | Explorer → Search box |
| Filter | Explorer → Column selector |
| Export | Settings → Tab 1 |
| Config | Settings → Tab 2 |

## 💾 Data Formats

**CSV**: Semicolon-delimited  
**JSON**: Pretty-printed records  
**Excel**: Multi-sheet with stats  

## ⚙️ Configuration

```powershell
# Alert thresholds (Settings → Configuration)
Critical: < 100
Low: 100-200
Medium: 200-500
Full: > 500

# Save config
Click "Save Thresholds" button
→ Creates dashboard_config.json
```

## 📊 Statistical Features

- Mean, Std, Min, Max
- Quartiles (Q1, Q2, Q3)
- IQR anomaly detection
- Rolling averages
- Time-based patterns
- Status transitions
- Critical event rate
- Health scoring

## 🎓 Learning Path

1. Run: `.\start-dashboard.ps1`
2. Browse: All 4 pages (5 min)
3. Try: Filters & export (5 min)
4. Read: `QUICK_START.md` (5 min)
5. Read: `DASHBOARD_FEATURES.md` (15 min)
6. Code: ESP8266 integration (30 min)

## ✅ Quick Test Checklist

- [ ] Dashboard loads (port 8501)
- [ ] All 4 pages accessible
- [ ] Charts render properly
- [ ] Filters work
- [ ] Export CSV works
- [ ] API responds (port 5000)
- [ ] Database connects (if used)
- [ ] ESP8266 sends data (if integrated)

## 🔐 Security Notes

- Default: No authentication
- API: No rate limiting
- DB: Change default password!
- Production: Add auth layer

## 🚀 Performance Tips

1. Use filters to reduce data
2. Adjust limit parameter
3. Cache auto-clears every 60s
4. Close unused browser tabs
5. Use pagination in Explorer

## 📞 Quick Help

**Issue**: Dashboard won't start  
**Fix**: Check if port 8501 is free

**Issue**: No data showing  
**Fix**: Check sensorWater.csv exists

**Issue**: DB connection error  
**Fix**: Verify docker-compose running

**Issue**: Import errors  
**Fix**: Activate venv + reinstall deps

## 🎉 Done!

Dashboard ready in 3 steps:
1. `.\start-dashboard.ps1`
2. Wait ~30 seconds
3. Browse to localhost:8501

**Enjoy! 🚀💧📊**
