import requests
from datetime import datetime

URL = 'http://127.0.0.1:5000/api/v1/sensor'

payload = {
    "device_id": "esp01",
    "ldr": 450,
    "water": 1,
    "buzzer": 0,
    "ts": datetime.utcnow().isoformat() + 'Z'
}

r = requests.post(URL, json=payload)
print(r.status_code, r.text)
