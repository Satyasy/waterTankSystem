# 📊 Dashboard Features Documentation

## Streamlit Advanced Dashboard - Complete Feature List

### 🎯 Main Navigation (4 Pages)

#### 1. 📊 Overview Dashboard
**Real-time monitoring dengan visualisasi utama**

**KPI Metrics:**
- Total Readings - jumlah pembacaan sensor
- Average Water Level - rata-rata level air dengan standar deviasi
- Critical Alerts - jumlah dan persentase alert kritis
- Max/Min Level - level tertinggi dan terendah

**Charts:**
- **Water Level Over Time** - Line chart interaktif dengan color coding berdasarkan status
  - Hover untuk detail
  - Zoom dan pan support
  - Multi-status visualization
  
- **Status Distribution** - Pie chart dengan breakdown:
  - CRITICAL (merah)
  - LOW (kuning)
  - MEDIUM (biru)
  - FULL (hijau)
  
- **Buzzer Activation** - Grouped bar chart
  - Aktivasi buzzer per status
  - Perbandingan buzzer ON/OFF
  
- **LED Status** - Stacked bar chart
  - Aktivitas LED berdasarkan LightStatus (NIGHT/DAY)
  
**Recent Critical Alerts Table:**
- 10 pembacaan kritis terbaru
- Sortir otomatis berdasarkan waktu

---

#### 2. 📈 Advanced Analytics
**Analisis mendalam dengan 4 sub-tabs**

**Tab 1: Statistical Analysis**
- **Water Level Statistics**
  - Mean, Std, Min, Max, Quartiles
  - Descriptive statistics table
  - Histogram with box plot overlay
  - Distribution analysis

- **Status Transition Analysis**
  - Sunburst chart untuk flow transisi status
  - Melihat pola perubahan status
  - Identifikasi transisi yang sering terjadi

**Tab 2: Anomaly Detection**
- **IQR Method (Interquartile Range)**
  - Automatic outlier detection
  - Visual scatter plot dengan anomalies highlighted
  - Upper/Lower bound lines
  - Anomaly count dan percentage
  - Recent anomalies table

**Tab 3: Trend Analysis**
- **Rolling Average**
  - Adjustable window size (5-50)
  - Smoothed trend line
  - Actual vs rolling average overlay
  
- **Time-based Patterns**
  - Water level by time periods
  - Mean dengan error bars (std deviation)
  - Identifikasi pola waktu

**Tab 4: Predictive Insights**
- **Critical Event Probability**
  - Gauge chart untuk critical alert rate
  - Color-coded threshold zones
  - Delta reference dari target 10%
  
- **Maintenance Recommendations**
  - Auto-generated recommendations berdasarkan data
  - Priority levels (HIGH/MEDIUM/LOW)
  - Actionable insights
  
- **System Health Score**
  - 0-100 score calculation
  - Visual progress bar
  - Health status: Excellent/Good/Fair/Poor

---

#### 3. 📋 Data Explorer
**Interactive data table dengan fitur lengkap**

**Features:**
- **Search Functionality**
  - Search dalam column tertentu
  - Case-insensitive search
  - Real-time filtering
  
- **Column Selector**
  - Pilih kolom mana yang ditampilkan
  - Multi-select support
  
- **Sorting**
  - Sort by any column
  - Ascending/Descending order
  
- **Pagination**
  - Adjustable rows per page (10-100)
  - Page navigation
  - Total records counter
  
- **Quick Statistics**
  - Toggle untuk tampilkan detailed statistics
  - Comprehensive describe() output

---

#### 4. ⚙️ Settings & Export
**Konfigurasi dan export data**

**Tab 1: Export Data**
- **CSV Export**
  - Standard comma-separated format
  - Timestamped filename
  - One-click download
  
- **JSON Export**
  - Pretty-printed JSON
  - Structured data format
  - API-friendly
  
- **Excel Export**
  - Multi-sheet workbook:
    - Sheet 1: Full sensor data
    - Sheet 2: Calculated statistics
  - Professional formatting
  
- **Filtered Export Option**
  - Export hanya data yang ter-filter
  - Respects current filters

**Tab 2: Configuration**
- **Alert Thresholds**
  - Configurable critical/low/medium/full thresholds
  - Save to JSON config file
  - Persistent settings
  
- **Display Settings**
  - Chart theme selector
  - Plotly themes: default, dark, simple_white

**Tab 3: System Info**
- **Data Source Status**
  - CSV availability check
  - Database connection status
  
- **Current Session Info**
  - Dashboard start time
  - Records loaded count
  
- **About Section**
  - Version information
  - Tech stack details
  
- **Cache Management**
  - Clear cache button
  - Force reload data

---

### 🎛️ Sidebar Controls

**Navigation:**
- Radio buttons untuk page selection
- Icons untuk visual cues

**Data Source Selection:**
- CSV File only
- Database only
- Both (Merged) - combines CSV + DB data

**Database Configuration:**
- Adjustable record limit (100-10,000)
- Merge status indicator

**Filters (Global):**
- **Status Filter** - Multi-select:
  - All
  - CRITICAL
  - LOW
  - MEDIUM
  - FULL
  
- **Water Level Range** - Slider:
  - Dynamic min/max based on data
  - Real-time filtering
  
- **Light Status** - Checkbox:
  - Filter NIGHT readings only

**Auto-refresh:**
- Toggle untuk enable/disable
- 30-second refresh interval
- Countdown indicator

---

### 🚀 Advanced Features

#### Data Integration
- **Dual Source Support**
  - Read from CSV file (sensorWater.csv)
  - Read from MariaDB database
  - Merge both sources seamlessly

#### Performance Optimization
- **Caching System**
  - `@st.cache_data` dengan 60s TTL
  - Fast data loading
  - Minimal re-computation

#### Interactivity
- **Plotly Charts**
  - Full interactivity (zoom, pan, hover)
  - Professional visualizations
  - Export chart as PNG
  - Responsive design

#### Error Handling
- Graceful degradation jika data source tidak tersedia
- Clear error messages
- Fallback options

#### Responsive Design
- Wide layout mode
- Adaptive column layouts
- Mobile-friendly (with limitations)

---

### 📊 Chart Types Used

1. **Line Chart** - Water level trends
2. **Pie Chart** - Status distribution
3. **Bar Chart** - Grouped dan stacked variants
4. **Scatter Plot** - Anomaly detection
5. **Histogram** - Distribution analysis
6. **Box Plot** - Statistical summary
7. **Sunburst Chart** - Hierarchical data
8. **Gauge Chart** - KPI indicators
9. **Area Chart** - Cumulative analysis (jika diperlukan)

---

### 🔧 Customization Options

**User Configurable:**
- Chart themes
- Alert thresholds
- Data limits
- Page size
- Refresh intervals
- Column visibility
- Filter combinations

**Developer Configurable (in code):**
- Color schemes
- Layout spacing
- Font styles
- Chart dimensions
- Statistical methods
- Anomaly detection algorithms

---

### 💡 Tips & Best Practices

1. **Performance:**
   - Gunakan filters untuk mengurangi data size
   - Cache akan auto-clear setiap 60 detik
   - Adjust DB limit sesuai kebutuhan

2. **Analysis:**
   - Gunakan Rolling Average untuk smooth trends
   - Check Anomaly Detection untuk outliers
   - Monitor Health Score secara rutin

3. **Export:**
   - Export filtered data untuk laporan spesifik
   - Excel export include statistics sheet
   - JSON untuk API integration

4. **Monitoring:**
   - Enable auto-refresh untuk real-time monitoring
   - Set appropriate thresholds untuk alerts
   - Check Recent Critical Alerts regularly

---

### 🎨 Color Coding

- **CRITICAL**: 🔴 Red (#ff4444) - Immediate attention
- **LOW**: 🟡 Yellow (#ffbb33) - Warning
- **MEDIUM**: 🔵 Blue (#33b5e5) - Normal operation
- **FULL**: 🟢 Green (#00C851) - Optimal
- **Anomaly**: 🔴 Red highlight
- **Normal**: 🔵 Blue default

---

### 🔄 Data Flow

```
CSV File / Database
        ↓
    Load Data
        ↓
   Apply Filters
        ↓
  Calculate Stats
        ↓
  Generate Charts
        ↓
  Render Dashboard
        ↓
   User Interaction
        ↓
  Update Display
```

---

## 🚀 Future Enhancement Ideas

- [ ] Real-time WebSocket connection ke ESP8266
- [ ] Email/SMS alerts untuk critical events
- [ ] Machine learning predictions
- [ ] Historical data comparison
- [ ] Multi-device dashboard
- [ ] User authentication
- [ ] Report scheduling
- [ ] API rate limiting
- [ ] Data backup automation
- [ ] Mobile app companion
