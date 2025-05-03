import time
import requests
from datetime import datetime

def check_service(name, url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"[{datetime.utcnow()}] ✅ {name} is healthy")
        else:
            print(f"[{datetime.utcnow()}] ⚠️ {name} unhealthy - Status {response.status_code}")
    except Exception as e:
        print(f"[{datetime.utcnow()}] ❌ {name} unreachable - {e}")

while True:
    check_service("Backend", "http://backend:8000/health")
    check_service("Notifier", "http://notifier:8500/health")
    time.sleep(30)
