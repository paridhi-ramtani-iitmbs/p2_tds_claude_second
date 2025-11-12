"""
Keep-Alive Script - Prevents Render from sleeping (prevents 599 errors)

Run this on a separate service (cron-job.org, uptimerobot.com, etc.)
Pings your service every 14 minutes to keep it awake
"""
import requests
import time
from datetime import datetime

# Replace with your Render URL
RENDER_URL = "https://your-app-name.onrender.com"
PING_INTERVAL = 840  # 14 minutes (Render free tier sleeps at 15 min)

def keep_alive():
    """Keep service alive"""
    while True:
        try:
            print(f"[{datetime.now()}] Pinging {RENDER_URL}/keepalive...")
            response = requests.get(f"{RENDER_URL}/keepalive", timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Service alive: {response.json()}")
            else:
                print(f"⚠️  Status: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print(f"Sleeping for {PING_INTERVAL} seconds...")
        time.sleep(PING_INTERVAL)

if __name__ == "__main__":
    print("🚀 Starting keep-alive service...")
    print(f"Will ping {RENDER_URL} every {PING_INTERVAL/60} minutes")
    keep_alive()
