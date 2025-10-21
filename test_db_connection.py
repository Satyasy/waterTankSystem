"""
Quick test script to verify database connection before upload
"""
import os
from datetime import datetime

print("=" * 60)
print("🔍 Database Connection Test")
print("=" * 60)

# Check .env file
print("\n1️⃣ Checking .env file...")
if os.path.exists('.env'):
    print("   ✅ .env file found")
    with open('.env', 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"   📄 Found {len(lines)} configuration lines")
else:
    print("   ⚠️  .env file not found - using defaults")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("   ✅ Environment variables loaded")
except Exception as e:
    print(f"   ⚠️  Could not load dotenv: {e}")

# Check database configuration
print("\n2️⃣ Database Configuration:")
db_config = {
    'DB_HOST': os.environ.get('DB_HOST', '127.0.0.1'),
    'DB_USER': os.environ.get('DB_USER', 'root'),
    'DB_PASS': os.environ.get('DB_PASS', '***' if os.environ.get('DB_PASS') else '(empty)'),
    'DB_NAME': os.environ.get('DB_NAME', 'iot_sensors'),
    'DB_PORT': os.environ.get('DB_PORT', '3306'),
}

for key, value in db_config.items():
    if key == 'DB_PASS':
        display_value = '***' if value != '(empty)' else '(empty)'
    else:
        display_value = value
    print(f"   {key}: {display_value}")

# Try to import mysql connector
print("\n3️⃣ Checking MySQL connector...")
try:
    import mysql.connector
    print("   ✅ mysql-connector-python is installed")
    print(f"   Version: {mysql.connector.__version__}")
except Exception as e:
    print(f"   ❌ mysql-connector-python not found: {e}")
    print("   Run: pip install mysql-connector-python")
    exit(1)

# Try to connect to database
print("\n4️⃣ Testing database connection...")
try:
    conn = mysql.connector.connect(
        host=os.environ.get('DB_HOST', '127.0.0.1'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASS', ''),
        port=int(os.environ.get('DB_PORT', 3306))
    )
    print("   ✅ Successfully connected to MySQL server")
    
    # Check if database exists
    cursor = conn.cursor()
    db_name = os.environ.get('DB_NAME', 'iot_sensors')
    cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
    result = cursor.fetchone()
    
    if result:
        print(f"   ✅ Database '{db_name}' exists")
        
        # Check if table exists
        cursor.execute(f"USE {db_name}")
        cursor.execute("SHOW TABLES LIKE 'sensor_readings'")
        table_result = cursor.fetchone()
        
        if table_result:
            print("   ✅ Table 'sensor_readings' exists")
            
            # Check table structure
            cursor.execute("DESCRIBE sensor_readings")
            columns = cursor.fetchall()
            print(f"   ✅ Table has {len(columns)} columns:")
            for col in columns:
                print(f"      - {col[0]} ({col[1]})")
            
            # Count existing records
            cursor.execute("SELECT COUNT(*) FROM sensor_readings")
            count = cursor.fetchone()[0]
            print(f"   📊 Current records in table: {count}")
            
        else:
            print("   ⚠️  Table 'sensor_readings' NOT found")
            print("   Please run: mysql -h 127.0.0.1 -u root -p < models.sql")
    else:
        print(f"   ⚠️  Database '{db_name}' NOT found")
        print("   Please run: mysql -h 127.0.0.1 -u root -p < models.sql")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as e:
    print(f"   ❌ Database connection failed: {e}")
    print("\n   Troubleshooting:")
    print("   - Is MySQL/MariaDB running? Check: docker ps")
    print("   - Is the password correct in .env?")
    print("   - Is the port correct? Default: 3306")
    print("   - Can you connect manually? Try: mysql -h 127.0.0.1 -u root -p")
    exit(1)

# Check CSV file
print("\n5️⃣ Checking CSV file...")
csv_file = 'sensorWater.csv'
if os.path.exists(csv_file):
    print(f"   ✅ {csv_file} found")
    
    # Read first few lines
    with open(csv_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"   📊 Total lines: {len(lines)}")
        print(f"   📋 Header: {lines[0].strip()}")
        if len(lines) > 1:
            print(f"   📋 Sample row: {lines[1].strip()}")
else:
    print(f"   ❌ {csv_file} not found")
    exit(1)

print("\n" + "=" * 60)
print("✅ ALL CHECKS PASSED - Ready to upload!")
print("=" * 60)
print("\nRun upload with:")
print("  python uploadData.py")
print("  python uploadData.py --clear  (to clear existing data first)")
