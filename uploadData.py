
import csv
import os
from datetime import datetime, timedelta
from db import get_db, init_pool

def parse_csv_row(row, base_timestamp=None):
    """
    Parse CSV row and convert to database format
    CSV columns: Time(s);WaterLevel;LightStatus;Status;LED;Buzzer
    """
    try:
        time_sec = int(row['Time(s)'])
        water_level = int(row['WaterLevel'])
        light_status = row['LightStatus'].strip().upper()
        status = row['Status'].strip().upper()
        
        # LED and Buzzer are already numeric (1/0) in your CSV
        led = int(row['LED'].strip())
        buzzer = int(row['Buzzer'].strip())
        
        # Generate timestamp based on Time(s) offset
        if base_timestamp:
            ts = base_timestamp + timedelta(seconds=time_sec)
        else:
            ts = datetime.utcnow() - timedelta(seconds=time_sec)
        
        # Map to database schema
        # LDR approximated from LightStatus (DAY/NIGHT or TERANG/GELAP)
        if light_status in ['NIGHT', 'GELAP', 'MALAM']:
            ldr_value = 200  # Low light
        elif light_status in ['DAY', 'TERANG', 'SIANG']:
            ldr_value = 800  # Bright light
        else:
            ldr_value = 500  # Default/unknown
        
        # Water sensor (1=detected, 0=not detected) based on water level or status
        if water_level > 0:
            water_detected = 1
        else:
            water_detected = 0
        
        return {
            'device_id': 'csv_import',
            'ldr': ldr_value,
            'water': water_detected,
            'buzzer': buzzer,
            'ts': ts,
            'water_level': water_level,  # Extra field for reference
            'status': status  # Extra field for reference
        }
    except Exception as e:
        print(f"❌ Error parsing row: {row}")
        print(f"   Error details: {e}")
        return None

def upload_csv_to_db(csv_file='sensorWater.csv', device_id='csv_import', batch_size=100, clear_existing=False):
    """
    Upload CSV data to database
    
    Args:
        csv_file: Path to CSV file
        device_id: Device identifier for all imported records
        batch_size: Number of records per batch insert
        clear_existing: If True, delete existing records for this device_id first
    """
    if not os.path.exists(csv_file):
        print(f"❌ Error: CSV file '{csv_file}' not found!")
        return False
    
    print(f"📂 Reading CSV file: {csv_file}")
    
    # Read CSV file
    rows = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        # Detect delimiter
        sample = f.read(1024)
        f.seek(0)
        delimiter = ';' if ';' in sample else ','
        
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)
    
    total_rows = len(rows)
    print(f"📊 Found {total_rows} records in CSV")
    
    if total_rows == 0:
        print("⚠️  No data to upload")
        return False
    
    # Initialize database pool
    print("🔌 Connecting to database...")
    try:
        init_pool()
        print("✅ Database connection initialized")
    except Exception as e:
        print(f"❌ Failed to initialize database connection: {e}")
        print("   Please check your .env file and database status")
        return False
    
    # Clear existing data if requested
    if clear_existing:
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sensor_readings WHERE device_id = %s", (device_id,))
            deleted = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            print(f"🗑️  Deleted {deleted} existing records for device '{device_id}'")
        except Exception as e:
            print(f"❌ Error clearing existing data: {e}")
            return False
    
    # Parse and insert data
    try:
        base_timestamp = datetime.utcnow() - timedelta(seconds=int(rows[-1]['Time(s)']))
    except Exception as e:
        print(f"⚠️  Warning: Could not calculate base timestamp: {e}")
        base_timestamp = datetime.utcnow()
    
    parsed_rows = []
    
    print("🔄 Parsing CSV data...")
    parse_errors = 0
    for row in rows:
        parsed = parse_csv_row(row, base_timestamp)
        if parsed:
            parsed['device_id'] = device_id
            parsed_rows.append(parsed)
        else:
            parse_errors += 1
    
    print(f"✅ Successfully parsed {len(parsed_rows)} records")
    if parse_errors > 0:
        print(f"⚠️  Skipped {parse_errors} records due to parse errors")
    
    if len(parsed_rows) == 0:
        print("❌ No valid records to upload after parsing")
        return False
    
    # Batch insert
    success_count = 0
    error_count = 0
    
    print(f"💾 Uploading to database (batch size: {batch_size})...")
    
    for i in range(0, len(parsed_rows), batch_size):
        batch = parsed_rows[i:i+batch_size]
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Prepare batch insert
            sql = """
                INSERT INTO sensor_readings (device_id, ldr, water, buzzer, ts)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            values = [
                (row['device_id'], row['ldr'], row['water'], row['buzzer'], row['ts'])
                for row in batch
            ]
            
            cursor.executemany(sql, values)
            conn.commit()
            success_count += cursor.rowcount
            
            cursor.close()
            conn.close()
            
            # Progress indicator
            progress = (i + len(batch)) / len(parsed_rows) * 100
            print(f"  Progress: {progress:.1f}% ({i + len(batch)}/{len(parsed_rows)})", end='\r')
            
        except Exception as e:
            error_count += len(batch)
            print(f"\n❌ Error inserting batch {i//batch_size + 1}: {e}")
            print(f"   Batch details: records {i} to {i+len(batch)-1}")
            import traceback
            traceback.print_exc()
            # Continue with next batch instead of stopping
    
    print(f"\n\n{'='*60}")
    print(f"📈 Upload Summary:")
    print(f"  Total records in CSV: {total_rows}")
    print(f"  Successfully uploaded: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Device ID: {device_id}")
    print(f"{'='*60}")
    
    return success_count > 0

def verify_upload(device_id='csv_import', limit=5):
    """Verify uploaded data by fetching latest records"""
    print(f"\n🔍 Verifying upload - fetching latest {limit} records...")
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM sensor_readings WHERE device_id = %s ORDER BY ts DESC LIMIT %s",
            (device_id, limit)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if rows:
            print(f"✅ Found {len(rows)} records. Latest entries:")
            print(f"\n{'ID':<8} {'Device':<15} {'LDR':<6} {'Water':<7} {'Buzzer':<8} {'Timestamp'}")
            print("-" * 80)
            for row in rows:
                print(f"{row['id']:<8} {row['device_id']:<15} {row['ldr']:<6} "
                      f"{row['water']:<7} {row['buzzer']:<8} {row['ts']}")
        else:
            print(f"⚠️  No records found for device '{device_id}'")
        
        return len(rows) > 0
    except Exception as e:
        print(f"❌ Error verifying upload: {e}")
        return False

def get_upload_stats(device_id='csv_import'):
    """Get statistics for uploaded data"""
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        # Total count
        cursor.execute(
            "SELECT COUNT(*) as total FROM sensor_readings WHERE device_id = %s",
            (device_id,)
        )
        total = cursor.fetchone()['total']
        
        # Date range
        cursor.execute(
            "SELECT MIN(ts) as first_ts, MAX(ts) as last_ts FROM sensor_readings WHERE device_id = %s",
            (device_id,)
        )
        date_range = cursor.fetchone()
        
        # Buzzer activations
        cursor.execute(
            "SELECT COUNT(*) as buzzer_on FROM sensor_readings WHERE device_id = %s AND buzzer = 1",
            (device_id,)
        )
        buzzer_count = cursor.fetchone()['buzzer_on']
        
        cursor.close()
        conn.close()
        
        print(f"\n📊 Database Statistics for '{device_id}':")
        print(f"  Total records: {total}")
        print(f"  Date range: {date_range['first_ts']} to {date_range['last_ts']}")
        print(f"  Buzzer activations: {buzzer_count}")
        
    except Exception as e:
        print(f"❌ Error fetching stats: {e}")

if __name__ == "__main__":
    import sys
    
    # Configuration
    CSV_FILE = 'sensorWater.csv'
    DEVICE_ID = 'csv_import'
    BATCH_SIZE = 100
    CLEAR_EXISTING = False  # Set to True to delete existing data first
    
    print("=" * 60)
    print("🚀 CSV to Database Uploader")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--clear':
            CLEAR_EXISTING = True
            print("⚠️  Mode: CLEAR existing data before upload")
        elif sys.argv[1] == '--help':
            print("\nUsage:")
            print("  python uploadData.py           # Normal upload")
            print("  python uploadData.py --clear   # Clear existing data first")
            print("  python uploadData.py --help    # Show this help")
            sys.exit(0)
    
    try:
        # Upload
        success = upload_csv_to_db(
            csv_file=CSV_FILE,
            device_id=DEVICE_ID,
            batch_size=BATCH_SIZE,
            clear_existing=CLEAR_EXISTING
        )
        
        if success:
            # Verify
            verify_upload(device_id=DEVICE_ID, limit=5)
            
            # Stats
            get_upload_stats(device_id=DEVICE_ID)
            
            print("\n✅ Upload completed successfully!")
        else:
            print("\n❌ Upload failed!")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Fatal error during upload: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)