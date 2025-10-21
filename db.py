import os
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:

    pass

try:
    import mysql.connector
    from mysql.connector import pooling
except Exception as e:

    raise ImportError("mysql-connector-python is required. Install with 'pip install mysql-connector-python'") from e

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASS', ''),
    'database': os.environ.get('DB_NAME', 'iot_sensors'),
    'port': int(os.environ.get('DB_PORT', 3306)),
}

pool = None

def init_pool():
    global pool
    if pool is None:
        pool = pooling.MySQLConnectionPool(pool_name="mypool",
                                           pool_size=int(os.environ.get('DB_POOL_SIZE', 5)),
                                           **DB_CONFIG)

def get_db():
    """Return a connection from pool. Caller should close the connection when done."""
    if pool is None:
        init_pool()
    return pool.get_connection()

def insert_reading(conn, device_id, ldr, water, buzzer, ts=None):
    if ts is None:
        ts = datetime.utcnow()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO sensor_readings (device_id, ldr, water, buzzer, ts)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (device_id, ldr, water, buzzer, ts)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def fetch_latest_readings(conn, device_id=None, limit=10):
    cursor = conn.cursor(dictionary=True)
    try:
        if device_id:
            cursor.execute(
                "SELECT * FROM sensor_readings WHERE device_id=%s ORDER BY ts DESC LIMIT %s",
                (device_id, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM sensor_readings ORDER BY ts DESC LIMIT %s",
                (limit,)
            )
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()
