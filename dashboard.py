import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json
from pathlib import Path

# Database integration (optional - if DB is configured)
try:
    from db import get_db, fetch_latest_readings
    DB_AVAILABLE = True
except Exception:
    DB_AVAILABLE = False

st.set_page_config(
    page_title="IoT Water Tank Monitoring",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .critical {
        background-color: #ff4444;
        padding: 5px 10px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }
    .warning {
        background-color: #ffbb33;
        padding: 5px 10px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }
    .normal {
        background-color: #00C851;
        padding: 5px 10px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def load_csv_data(csv_path='sensorWater.csv'):
    """Load and parse CSV data with caching"""
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    
    df = pd.read_csv(csv_path, delimiter=';')
    
    # Clean and convert data types
    if 'Time(s)' in df.columns:
        df['Time(s)'] = pd.to_numeric(df['Time(s)'], errors='coerce')
    if 'WaterLevel' in df.columns:
        df['WaterLevel'] = pd.to_numeric(df['WaterLevel'], errors='coerce')
    if 'LED' in df.columns:
        df['LED'] = pd.to_numeric(df['LED'], errors='coerce')
    if 'Buzzer' in df.columns:
        df['Buzzer'] = pd.to_numeric(df['Buzzer'], errors='coerce')
    
    # Add computed columns
    df['Timestamp'] = pd.to_datetime('now') - pd.to_timedelta(df['Time(s)'].max() - df['Time(s)'], unit='s')
    
    return df


def load_db_data(limit=1000):
    """Load data from database if available"""
    if not DB_AVAILABLE:
        return pd.DataFrame()
    
    try:
        conn = get_db()
        rows = fetch_latest_readings(conn, limit=limit)
        if rows:
            df = pd.DataFrame(rows)
            # Rename columns to match CSV format
            df = df.rename(columns={
                'ldr': 'LDR',
                'water': 'WaterSensor',
                'buzzer': 'Buzzer',
                'ts': 'Timestamp',
                'device_id': 'DeviceID'
            })
            return df
        return pd.DataFrame()
    except Exception as e:
        st.sidebar.error(f"DB Error: {e}")
        return pd.DataFrame()


def calculate_statistics(df):
    """Calculate comprehensive statistics"""
    if df.empty:
        return {}
    
    stats = {
        'total_readings': len(df),
        'avg_water_level': df['WaterLevel'].mean() if 'WaterLevel' in df.columns else 0,
        'min_water_level': df['WaterLevel'].min() if 'WaterLevel' in df.columns else 0,
        'max_water_level': df['WaterLevel'].max() if 'WaterLevel' in df.columns else 0,
        'std_water_level': df['WaterLevel'].std() if 'WaterLevel' in df.columns else 0,
        'critical_count': len(df[df['Status'] == 'CRITICAL']) if 'Status' in df.columns else 0,
        'low_count': len(df[df['Status'] == 'LOW']) if 'Status' in df.columns else 0,
        'medium_count': len(df[df['Status'] == 'MEDIUM']) if 'Status' in df.columns else 0,
        'full_count': len(df[df['Status'] == 'FULL']) if 'Status' in df.columns else 0,
        'buzzer_active_count': len(df[df['Buzzer'] == 1]) if 'Buzzer' in df.columns else 0,
        'night_readings': len(df[df['LightStatus'] == 'NIGHT']) if 'LightStatus' in df.columns else 0,
    }
    
    return stats


def main():
    st.markdown('<div class="main-header">💧 IoT Water Tank Monitoring System</div>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🎛️ Control Panel")
    page = st.sidebar.radio(
        "Navigation",
        ["📊 Overview Dashboard", "📈 Advanced Analytics", "📋 Data Explorer", "⚙️ Settings & Export"]
    )
    
    # Data source selection
    st.sidebar.markdown("---")
    st.sidebar.subheader("Data Source")
    data_source = st.sidebar.radio("Select Source", ["CSV File", "Database", "Both (Merged)"])
    
    # Load data based on selection
    df_csv = load_csv_data()
    df_db = pd.DataFrame()
    
    if data_source in ["Database", "Both (Merged)"] and DB_AVAILABLE:
        db_limit = st.sidebar.number_input("DB Records Limit", 100, 10000, 1000)
        df_db = load_db_data(limit=db_limit)
    
    # Merge data if needed
    if data_source == "Both (Merged)" and not df_db.empty and not df_csv.empty:
        df = pd.concat([df_csv, df_db], ignore_index=True)
        st.sidebar.success(f"✅ Merged {len(df_csv)} CSV + {len(df_db)} DB records")
    elif data_source == "Database":
        df = df_db
    else:
        df = df_csv
    
    if df.empty:
        st.error("⚠️ No data available. Please check your data source.")
        return
    
    # Filters
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filters")
    
    # Status filter
    if 'Status' in df.columns:
        status_options = ['All'] + sorted(df['Status'].dropna().unique().tolist())
        selected_status = st.sidebar.multiselect("Status", status_options, default=['All'])
        if 'All' not in selected_status:
            df = df[df['Status'].isin(selected_status)]
    
    # Water level range filter
    if 'WaterLevel' in df.columns:
        min_level, max_level = int(df['WaterLevel'].min()), int(df['WaterLevel'].max())
        level_range = st.sidebar.slider(
            "Water Level Range",
            min_level, max_level,
            (min_level, max_level)
        )
        df = df[(df['WaterLevel'] >= level_range[0]) & (df['WaterLevel'] <= level_range[1])]
    
    # Light status filter
    if 'LightStatus' in df.columns:
        light_filter = st.sidebar.checkbox("Night Only", value=False)
        if light_filter:
            df = df[df['LightStatus'] == 'NIGHT']
    
    # Auto-refresh option
    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)")
    if auto_refresh:
        st.sidebar.info("Dashboard will refresh in 30 seconds")
        # This triggers a rerun after 30 seconds
        import time
        time.sleep(30)
        st.rerun()
    
    # Page routing
    if page == "📊 Overview Dashboard":
        show_overview_dashboard(df)
    elif page == "📈 Advanced Analytics":
        show_advanced_analytics(df)
    elif page == "📋 Data Explorer":
        show_data_explorer(df)
    elif page == "⚙️ Settings & Export":
        show_settings_export(df)


def show_overview_dashboard(df):
    """Main overview dashboard with key metrics and charts"""
    st.header("📊 Real-Time Overview")
    
    # Calculate statistics
    stats = calculate_statistics(df)
    
    # KPI Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Readings", f"{stats['total_readings']:,}")
    
    with col2:
        st.metric(
            "Avg Water Level",
            f"{stats['avg_water_level']:.1f}",
            delta=f"±{stats['std_water_level']:.1f}"
        )
    
    with col3:
        critical_pct = (stats['critical_count'] / stats['total_readings'] * 100) if stats['total_readings'] > 0 else 0
        st.metric("Critical Alerts", stats['critical_count'], delta=f"{critical_pct:.1f}%", delta_color="inverse")
    
    with col4:
        st.metric("Max Level", f"{stats['max_water_level']:.0f}")
    
    with col5:
        st.metric("Min Level", f"{stats['min_water_level']:.0f}")
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💧 Water Level Over Time")
        if 'WaterLevel' in df.columns and 'Time(s)' in df.columns:
            fig = px.line(
                df.sort_values('Time(s)'),
                x='Time(s)',
                y='WaterLevel',
                color='Status' if 'Status' in df.columns else None,
                title="Water Level Trend",
                markers=True
            )
            fig.update_layout(height=400, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Status Distribution")
        if 'Status' in df.columns:
            status_counts = df['Status'].value_counts()
            colors = {'CRITICAL': '#ff4444', 'LOW': '#ffbb33', 'MEDIUM': '#33b5e5', 'FULL': '#00C851'}
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Status Breakdown",
                color=status_counts.index,
                color_discrete_map=colors
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔔 Buzzer Activation")
        if 'Buzzer' in df.columns:
            buzzer_data = df.groupby(['Status', 'Buzzer']).size().reset_index(name='count')
            fig = px.bar(
                buzzer_data,
                x='Status',
                y='count',
                color='Buzzer',
                title="Buzzer Status by Water Level",
                barmode='group',
                color_discrete_map={0: '#00C851', 1: '#ff4444'}
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💡 LED Status")
        if 'LED' in df.columns and 'LightStatus' in df.columns:
            led_data = df.groupby(['LightStatus', 'LED']).size().reset_index(name='count')
            fig = px.bar(
                led_data,
                x='LightStatus',
                y='count',
                color='LED',
                title="LED Activity by Light Status",
                barmode='stack'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent alerts
    st.markdown("---")
    st.subheader("⚠️ Recent Critical Alerts")
    if 'Status' in df.columns:
        critical_df = df[df['Status'] == 'CRITICAL'].tail(10)
        if not critical_df.empty:
            st.dataframe(
                critical_df[['Time(s)', 'WaterLevel', 'Status', 'LED', 'Buzzer']].sort_values('Time(s)', ascending=False),
                use_container_width=True
            )
        else:
            st.success("✅ No critical alerts in current dataset!")


def show_advanced_analytics(df):
    """Advanced analytics with statistical insights"""
    st.header("📈 Advanced Analytics")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Statistical Analysis", "🔍 Anomaly Detection", "📉 Trend Analysis", "🎯 Predictive Insights"])
    
    with tab1:
        st.subheader("Statistical Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Water Level Statistics")
            if 'WaterLevel' in df.columns:
                stats_df = df['WaterLevel'].describe().to_frame()
                st.dataframe(stats_df, use_container_width=True)
                
                # Histogram
                fig = px.histogram(
                    df,
                    x='WaterLevel',
                    nbins=50,
                    title="Water Level Distribution",
                    marginal="box"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Status Transition Analysis")
            if 'Status' in df.columns and 'Time(s)' in df.columns:
                # Status transitions
                df_sorted = df.sort_values('Time(s)')
                df_sorted['PrevStatus'] = df_sorted['Status'].shift(1)
                transitions = df_sorted.groupby(['PrevStatus', 'Status']).size().reset_index(name='count')
                
                if not transitions.empty:
                    fig = px.sunburst(
                        transitions,
                        path=['PrevStatus', 'Status'],
                        values='count',
                        title="Status Transition Flow"
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("🔍 Anomaly Detection")
        
        if 'WaterLevel' in df.columns:
            # Simple anomaly detection using IQR
            Q1 = df['WaterLevel'].quantile(0.25)
            Q3 = df['WaterLevel'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            df['Anomaly'] = ((df['WaterLevel'] < lower_bound) | (df['WaterLevel'] > upper_bound))
            anomalies = df[df['Anomaly'] == True]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.scatter(
                    df.sort_values('Time(s)'),
                    x='Time(s)',
                    y='WaterLevel',
                    color='Anomaly',
                    title="Anomaly Detection (IQR Method)",
                    color_discrete_map={True: '#ff4444', False: '#33b5e5'}
                )
                fig.add_hline(y=upper_bound, line_dash="dash", line_color="red", annotation_text="Upper Bound")
                fig.add_hline(y=lower_bound, line_dash="dash", line_color="red", annotation_text="Lower Bound")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Anomalies Detected", len(anomalies))
                st.metric("% Anomalous", f"{len(anomalies)/len(df)*100:.2f}%")
                
                if not anomalies.empty:
                    st.markdown("#### Recent Anomalies")
                    st.dataframe(
                        anomalies[['Time(s)', 'WaterLevel', 'Status']].tail(5),
                        use_container_width=True
                    )
    
    with tab3:
        st.subheader("📉 Trend Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'WaterLevel' in df.columns and 'Time(s)' in df.columns:
                # Rolling average
                window_size = st.slider("Rolling Window Size", 5, 50, 10)
                df_sorted = df.sort_values('Time(s)')
                df_sorted['RollingAvg'] = df_sorted['WaterLevel'].rolling(window=window_size).mean()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_sorted['Time(s)'],
                    y=df_sorted['WaterLevel'],
                    mode='markers',
                    name='Actual',
                    opacity=0.5
                ))
                fig.add_trace(go.Scatter(
                    x=df_sorted['Time(s)'],
                    y=df_sorted['RollingAvg'],
                    mode='lines',
                    name=f'Rolling Avg ({window_size})',
                    line=dict(color='red', width=3)
                ))
                fig.update_layout(title="Water Level with Rolling Average", height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Time(s)' in df.columns:
                # Time-based patterns
                df_sorted = df.sort_values('Time(s)')
                df_sorted['TimeGroup'] = pd.cut(df_sorted['Time(s)'], bins=10)
                time_stats = df_sorted.groupby('TimeGroup')['WaterLevel'].agg(['mean', 'std', 'count'])
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=time_stats.index.astype(str),
                    y=time_stats['mean'],
                    error_y=dict(type='data', array=time_stats['std']),
                    name='Mean ± Std'
                ))
                fig.update_layout(title="Water Level by Time Period", height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("🎯 Predictive Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Critical Event Probability")
            if 'Status' in df.columns:
                critical_rate = len(df[df['Status'] == 'CRITICAL']) / len(df) * 100
                
                # Gauge chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=critical_rate,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Critical Alert Rate (%)"},
                    delta={'reference': 10},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 25], 'color': "lightgreen"},
                            {'range': [25, 50], 'color': "yellow"},
                            {'range': [50, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 50
                        }
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Maintenance Recommendations")
            
            recommendations = []
            if 'Status' in df.columns:
                critical_count = len(df[df['Status'] == 'CRITICAL'])
                if critical_count > len(df) * 0.3:
                    recommendations.append("🔴 HIGH: Frequent critical alerts detected. Check water supply system.")
                
                full_count = len(df[df['Status'] == 'FULL'])
                if full_count < len(df) * 0.1:
                    recommendations.append("🟡 MEDIUM: Low frequency of full tank status. Verify fill mechanism.")
            
            if 'Buzzer' in df.columns:
                buzzer_active = len(df[df['Buzzer'] == 1])
                if buzzer_active > len(df) * 0.5:
                    recommendations.append("🟠 MEDIUM: Buzzer frequently active. Consider adjusting alert thresholds.")
            
            if not recommendations:
                recommendations.append("✅ System operating within normal parameters.")
            
            for rec in recommendations:
                st.info(rec)
            
            # Next predicted event
            st.markdown("#### System Health Score")
            health_score = 100 - (critical_rate * 0.8)
            health_score = max(0, min(100, health_score))
            
            progress_color = "green" if health_score > 70 else "orange" if health_score > 40 else "red"
            st.progress(health_score / 100)
            st.markdown(f"**Score: {health_score:.1f}/100** - System health is **{'Excellent' if health_score > 80 else 'Good' if health_score > 60 else 'Fair' if health_score > 40 else 'Poor'}**")


def show_data_explorer(df):
    """Interactive data explorer with search and filtering"""
    st.header("📋 Data Explorer")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Records", len(df))
    
    with col2:
        if 'Time(s)' in df.columns:
            time_range = f"{df['Time(s)'].min():.0f}s - {df['Time(s)'].max():.0f}s"
            st.metric("Time Range", time_range)
    
    with col3:
        columns_count = len(df.columns)
        st.metric("Columns", columns_count)
    
    st.markdown("---")
    
    # Search functionality
    search_col = st.selectbox("Search in column", df.columns.tolist())
    search_term = st.text_input("Search term")
    
    if search_term:
        df = df[df[search_col].astype(str).str.contains(search_term, case=False, na=False)]
        st.info(f"Found {len(df)} matching records")
    
    # Column selector
    st.subheader("Select Columns to Display")
    selected_columns = st.multiselect(
        "Columns",
        df.columns.tolist(),
        default=df.columns.tolist()
    )
    
    # Sorting
    col1, col2 = st.columns(2)
    with col1:
        sort_column = st.selectbox("Sort by", df.columns.tolist())
    with col2:
        sort_order = st.radio("Order", ["Ascending", "Descending"])
    
    df_display = df[selected_columns].sort_values(
        by=sort_column,
        ascending=(sort_order == "Ascending")
    )
    
    # Pagination
    rows_per_page = st.slider("Rows per page", 10, 100, 25)
    total_pages = len(df_display) // rows_per_page + (1 if len(df_display) % rows_per_page > 0 else 0)
    page_num = st.number_input("Page", 1, max(1, total_pages), 1)
    
    start_idx = (page_num - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    
    st.dataframe(
        df_display.iloc[start_idx:end_idx],
        use_container_width=True,
        height=500
    )
    
    st.caption(f"Showing {start_idx + 1}-{min(end_idx, len(df_display))} of {len(df_display)} records")
    
    # Quick statistics
    st.markdown("---")
    st.subheader("Quick Statistics")
    
    if st.checkbox("Show detailed statistics"):
        st.dataframe(df.describe(), use_container_width=True)


def show_settings_export(df):
    """Settings and data export functionality"""
    st.header("⚙️ Settings & Export")
    
    tab1, tab2, tab3 = st.tabs(["📥 Export Data", "⚙️ Configuration", "ℹ️ System Info"])
    
    with tab1:
        st.subheader("Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### CSV Export")
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
            
            st.markdown("### JSON Export")
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="⬇️ Download JSON",
                data=json_data,
                file_name=f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
            )
        
        with col2:
            st.markdown("### Excel Export")
            # For Excel, we need to use BytesIO
            from io import BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='SensorData')
                
                # Add statistics sheet
                stats_df = pd.DataFrame([calculate_statistics(df)]).T
                stats_df.columns = ['Value']
                stats_df.to_excel(writer, sheet_name='Statistics')
            
            st.download_button(
                label="⬇️ Download Excel",
                data=buffer.getvalue(),
                file_name=f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.ms-excel"
            )
            
            st.markdown("### Filtered Data Only")
            filter_export = st.checkbox("Export only filtered/displayed data")
            if filter_export:
                st.info(f"Will export {len(df)} records (filtered)")
    
    with tab2:
        st.subheader("Dashboard Configuration")
        
        st.markdown("#### Alert Thresholds")
        col1, col2 = st.columns(2)
        
        with col1:
            critical_threshold = st.number_input("Critical Level Threshold", 0, 1000, 100)
            low_threshold = st.number_input("Low Level Threshold", 0, 1000, 200)
        
        with col2:
            medium_threshold = st.number_input("Medium Level Threshold", 0, 1000, 400)
            full_threshold = st.number_input("Full Level Threshold", 0, 1000, 500)
        
        if st.button("💾 Save Thresholds"):
            # Save to config file
            config = {
                'thresholds': {
                    'critical': critical_threshold,
                    'low': low_threshold,
                    'medium': medium_threshold,
                    'full': full_threshold
                }
            }
            with open('dashboard_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            st.success("✅ Configuration saved!")
        
        st.markdown("#### Display Settings")
        theme = st.selectbox("Chart Theme", ["plotly", "plotly_dark", "simple_white"])
        st.info(f"Selected theme: {theme}")
    
    with tab3:
        st.subheader("System Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Data Source")
            st.info(f"CSV File: {'✅ Available' if os.path.exists('sensorWater.csv') else '❌ Not found'}")
            st.info(f"Database: {'✅ Connected' if DB_AVAILABLE else '❌ Not configured'}")
            
            st.markdown("#### Current Session")
            st.info(f"Dashboard Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.info(f"Records Loaded: {len(df)}")
        
        with col2:
            st.markdown("#### About")
            st.info("**IoT Water Tank Monitoring Dashboard**")
            st.info("Version: 1.0.0")
            st.info("Built with: Streamlit + Plotly")
            st.info("Data: ESP8266 Sensors")
            
            if st.button("🔄 Clear Cache & Reload"):
                st.cache_data.clear()
                st.rerun()


if __name__ == "__main__":
    main()
