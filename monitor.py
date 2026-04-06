import requests
import time
import os
from datetime import datetime

# Import local helpers (assuming they are in the same dir or PYTHONPATH)
from pymongo import MongoClient
from memory.retention import calculate_retention_from_timestamp

# MongoDB Connection (Local instance for monitor)
client = MongoClient("mongodb://localhost:27017")
db = client["bigfive"]
collection = db["ocean_scores"]

def get_retention_status(retention):
    if retention >= 0.40: return {"level": "clear", "emoji": "✅"}
    if retention >= 0.30: return {"level": "uncertain", "emoji": "⚠️"}
    return {"level": "reconstruction", "emoji": "🛑"}

def watch_degradation(report_id, game_time_scale=60):
    """
    1 minute real time = 1 game day.
    Displays time in Days, Hours, Minutes.
    Stops at 30% retention.
    """
    last_day_announced = 0

    while True:
        candidate = collection.find_one({"report_id": report_id})
        if not candidate:
            print("❌ Candidate not found.")
            break

        created_at = datetime.fromisoformat(candidate["saved_at"])
        retention, debug, phase = calculate_retention_from_timestamp(
            p_factor=candidate["p_factor"],
            created_at=created_at,
            game_time_scale=game_time_scale
        )

        g_days_raw = debug["game_days"] # This is the decimal (e.g. 0.81)
        real_secs = debug['real_seconds']
        interpretation = get_retention_status(retention)

        # --- CONVERT DECIMAL TO CLOCK TIME ---
        # 1.0 g_days = 24 hours
        total_game_hours = g_days_raw * 24
        
        display_days = int(g_days_raw)
        display_hours = int(total_game_hours % 24)
        display_minutes = int((total_game_hours * 60) % 60)

        # Notify when a full day passes
        current_day_int = int(g_days_raw)
        if current_day_int > last_day_announced:
            print(f"\n🔔 NEW DAY: Day {current_day_int} has started!")
            print(f"🧠 TRIGGERING LINGUISTIC ENGINE...")
            
            try:
                # Trigger linguistic generation via API
                port = os.getenv("PORT", "8000")
                resp = requests.post(f"http://localhost:{port}/api/generate-npc-response/{report_id}")
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"🗣️ NPC SAYS: {data['response']}")
                else:
                    print(f"❌ Generation failed: {resp.status_code}")
            except Exception as e:
                print(f"❌ API Error: {str(e)}")
            
            last_day_announced = current_day_int
            time.sleep(1)

        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Real Timer for your reference
        mins = int(real_secs // 60)
        secs = int(real_secs % 60)

        print("="*50)
        print(f"🧠 MADE ENGINE: LIVE DEGRADATION MONITOR")
        print("="*50)
        print(f"Report ID:    {report_id}")
        
        # This now shows as a clock: e.g., Day 0 | 18:30
        print(f"Game Clock:   Day {display_days} | {display_hours:02d}:{display_minutes:02d}") 
        print(f"Real Timer:   {mins}m {secs}s (60s = 1 Day)")
        print(f"P-Factor:     {status['p_factor']:.4f}")
        print(f"RETENTION:    {retention*100:.2f}% {interpretation['emoji']}")
        print(f"STATUS:       {interpretation['level'].upper()}")
        print("-"*50)

        bar_length = 20
        filled = int(retention * bar_length)
        bar = "█" * filled + "-" * (bar_length - filled)
        print(f"[{bar}]")

        if retention <= 0.30:
            print(f"\n🛑 THRESHOLD REACHED: Memory degraded to 21%.")
            print(f"📅 Total Time: Day {display_days}, {display_hours}h {display_minutes}m")
            print(f"⚠️  Reconstruction is now required.")
            break

        time.sleep(1)