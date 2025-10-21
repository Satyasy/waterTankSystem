# 🚀 Quick Reference Guide

## Cara Cepat Menjalankan Dashboard

### Method 1: Menggunakan Script PowerShell (Paling Mudah)
```powershell
.\start-dashboard.ps1
```
Script ini akan otomatis:
- Membuat virtual environment jika belum ada
- Install semua dependencies
- Launch Streamlit dashboard

### Method 2: Manual Step-by-Step
```powershell
# 1. Buat virtual environment
python -m venv .venv

# 2. Activate
.\\.venv\\Scripts\\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run dashboard
streamlit run dashboard.py
```

---

## 📊 Fitur Dashboard Utama

### 4 Halaman Utama:

1. **📊 Overview Dashboard**
   - KPI metrics real-time
   - Water level trends
   - Status distribution pie chart
   - Buzzer & LED status charts
   - Recent critical alerts

2. **📈 Advanced Analytics**
   - Statistical analysis
   - Anomaly detection (IQR method)
   - Trend analysis dengan rolling average
   - Predictive insights & health score

3. **📋 Data Explorer**
   - Interactive data table
   - Search, filter, sort
   - Pagination
   - Quick statistics

4. **⚙️ Settings & Export**
   - Export CSV/JSON/Excel
   - Configure alert thresholds
   - System information
   - Cache management

---

## 🎛️ Sidebar Controls

### Data Source:
- **CSV File** - Baca dari sensorWater.csv
- **Database** - Baca dari MariaDB
- **Both (Merged)** - Gabung keduanya

### Filters:
- Status (multi-select)
- Water level range (slider)
- Light status (night only)
- Auto-refresh (30s)

---

## 📡 Flask API (Backend)

### Jalankan API Server:
```powershell
python main.py
```

### Endpoints:
- `POST /api/v1/sensor` - Kirim data dari ESP8266
- `GET /api/v1/sensor/latest` - Ambil data terbaru dari DB
- `GET /api/v1/csv` - Baca data dari CSV dengan filter

### Test API:
```powershell
# Send test data
python send_test.py

# Query latest
curl http://127.0.0.1:5000/api/v1/sensor/latest?limit=10

# Query CSV
curl http://127.0.0.1:5000/api/v1/csv?status=CRITICAL
```

---

## 🔌 ESP8266 Integration

### Arduino Code Snippet:
```cpp
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* server = "http://YOUR_SERVER_IP:5000/api/v1/sensor";

void loop(){
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(server);
    http.addHeader("Content-Type", "application/json");
    
    String payload = "{";
    payload += "\"device_id\":\"esp01\",";
    payload += "\"ldr\":" + String(analogRead(A0)) + ",";
    payload += "\"water\":" + String(digitalRead(D1)) + ",";
    payload += "\"buzzer\":" + String(digitalRead(D2));
    payload += "}";
    
    int code = http.POST(payload);
    http.end();
  }
  delay(60000); // 1 minute
}
```

---

## 🗄️ Database Setup (Optional)

### Dengan Docker Compose:
```powershell
# Start MariaDB
docker-compose up -d

# Create schema
mysql -h 127.0.0.1 -P 3306 -u root -pexample < models.sql

# Check status
docker-compose ps
```

### Manual MariaDB:
1. Install MariaDB/MySQL
2. Create database: `iot_sensors`
3. Run `models.sql` script
4. Set environment variables:
   ```powershell
   $env:DB_HOST='127.0.0.1'
   $env:DB_USER='root'
   $env:DB_PASS='yourpassword'
   $env:DB_NAME='iot_sensors'
   ```

---

## 📁 File Structure

```
waterTankSystemMonitoring/
├── dashboard.py              # Streamlit dashboard (MAIN)
├── main.py                   # Flask API server
├── db.py                     # Database helper
├── models.sql                # Database schema
├── sensorWater.csv           # Sample data
├── send_test.py              # API test client
├── requirements.txt          # Dependencies
├── docker-compose.yml        # MariaDB container
├── .env.example              # Environment vars template
├── start-dashboard.ps1       # Quick start script
├── README.md                 # Full documentation
├── DASHBOARD_FEATURES.md     # Feature details
├── .streamlit/
│   └── config.toml           # Streamlit config
└── templates/
    └── dashboard.html        # Legacy HTML dashboard
```

---

## 🎯 Common Tasks

### Export Data dari Dashboard:
1. Buka Settings & Export page
2. Pilih format (CSV/JSON/Excel)
3. Klik Download button

### Filter Data Spesifik:
1. Gunakan sidebar filters
2. Pilih status yang diinginkan
3. Adjust water level range
4. Data otomatis ter-filter

### Lihat Anomalies:
1. Buka Advanced Analytics
2. Tab "Anomaly Detection"
3. Lihat scatter plot dengan red highlights

### Configure Alert Thresholds:
1. Buka Settings & Export
2. Tab "Configuration"
3. Set nilai threshold
4. Klik Save

### Auto-refresh Dashboard:
1. Buka sidebar
2. Check "Auto-refresh (30s)"
3. Dashboard akan reload otomatis

---

## 🐛 Troubleshooting

### Dashboard tidak muncul?
```powershell
# Check if port 8501 sudah digunakan
netstat -ano | findstr :8501

# Kill process jika perlu
taskkill /PID <PID> /F

# Restart dashboard
streamlit run dashboard.py
```

### Error "Import streamlit could not be resolved"?
```powershell
# Pastikan virtual environment aktif
.\\.venv\\Scripts\\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Data tidak muncul?
1. Check apakah `sensorWater.csv` ada
2. Check format CSV (delimiter: semicolon)
3. Check database connection jika pakai DB mode
4. Clear cache: Settings → Clear Cache & Reload

### Database connection error?
1. Pastikan MariaDB running
2. Check environment variables
3. Test connection: `mysql -h 127.0.0.1 -u root -p`
4. Verify credentials di `.env`

---

## 📊 Data Format

### CSV Format (sensorWater.csv):
```csv
Time(s);WaterLevel;LightStatus;Status;LED;Buzzer
154;8;NIGHT;CRITICAL;1;1
155;9;NIGHT;CRITICAL;1;1
```

### API Payload Format (ESP8266 → Server):
```json
{
  "device_id": "esp01",
  "ldr": 450,
  "water": 1,
  "buzzer": 0,
  "ts": "2025-10-21T12:34:56Z"
}
```

### Database Schema:
```sql
CREATE TABLE sensor_readings (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  device_id VARCHAR(64) NOT NULL,
  ldr INT NULL,
  water TINYINT(1) NULL,
  buzzer TINYINT(1) NULL,
  ts DATETIME NOT NULL,
  INDEX idx_device_ts (device_id, ts)
);
```

---

## 💡 Tips & Best Practices

1. **Performance**: Gunakan filter untuk mengurangi data load
2. **Monitoring**: Enable auto-refresh untuk real-time monitoring
3. **Analysis**: Check anomaly detection regularly
4. **Export**: Export filtered data untuk laporan spesifik
5. **Thresholds**: Adjust alert thresholds sesuai kebutuhan sistem Anda
6. **Backup**: Export data secara berkala untuk backup

---

## 🔗 Useful Links

- **Streamlit Docs**: https://docs.streamlit.io
- **Plotly Docs**: https://plotly.com/python/
- **Flask Docs**: https://flask.palletsprojects.com/
- **ESP8266 Docs**: https://arduino-esp8266.readthedocs.io/

---

## 📞 Support

Untuk dokumentasi lengkap, lihat:
- `README.md` - Setup lengkap dan ESP8266 integration
- `DASHBOARD_FEATURES.md` - Detail semua fitur dashboard
- `models.sql` - Database schema reference
