import math
import time
import sys
from datetime import datetime, timezone
from pymongo import MongoClient

# Research-Validated Constants
S_FAST = 1.47   # Yadav (2025) Fast decay
S_SLOW = 4.07   # Yadav (2025) Slow decay  
TRANSITION_THRESHOLD = 0.40  # Kornell et al. (2011)
STOP_THRESHOLD = 0.30        # Parks & Yonelinas (2009)

def calculate_retention(p_factor, days=0, s_fast=None, s_slow=None, **kwargs):
   
    # Use priority-based S values if provided, otherwise use defaults
    s_f = s_fast if s_fast is not None else S_FAST
    s_s = s_slow if s_slow is not None else S_SLOW
    
    days = max(0, days)
    
    # PHASE 1: Fast decay until 40%
    r_fast = p_factor * math.exp(-days / s_f)
    
    if r_fast >= TRANSITION_THRESHOLD:
        return round(r_fast, 4), "Phase 1 (Fast)", days
    
    # EXACT transition time
    t_transition = -s_f * math.log(TRANSITION_THRESHOLD / p_factor)
    
    # PHASE 2: Continue from EXACT transition point
    time_in_slow = days - t_transition
    r_slow = TRANSITION_THRESHOLD * math.exp(-time_in_slow / s_s)
    
    return round(max(STOP_THRESHOLD, r_slow), 4), "Phase 2 (Slow)", time_in_slow

def calculate_retention_from_timestamp(p_factor, created_at, game_time_scale=60, **kwargs):
    """Convert real time → game days. Accepts **kwargs."""
    time_delta = datetime.now(timezone.utc) - created_at
    real_seconds = time_delta.total_seconds()
    game_days = real_seconds / game_time_scale  # 60sec = 1 game day
    
    retention, phase, slow_time = calculate_retention(p_factor, game_days)
    
    return retention, {
        "game_days": round(game_days, 2),
        "real_seconds": int(real_seconds),
        "phase": phase,
        "slow_time": round(slow_time, 2) if phase == "Phase 2 (Slow)" else 0
    }, phase

def start_monitor(report_id):
    client = MongoClient("mongodb://localhost:27017")
    db = client["bigfive"]
    collection = db["ocean_scores"]
    candidate = collection.find_one({"report_id": report_id})

    if not candidate:
        print(" Report ID not found!")
        return

    p_factor = candidate["p_factor"]
    start_time = datetime.fromisoformat(candidate.get("saved_at", datetime.now(timezone.utc).isoformat()))

    print(f"\n TWO-PHASE MONITOR STARTED | ID: {report_id}")
    print(f" P-Factor: {p_factor:.2f} ({p_factor*100:.0f}%)")
    print(f" S_FAST: {S_FAST:.2f} | S_SLOW: {S_SLOW:.2f}")
    print(f" Transition: {TRANSITION_THRESHOLD*100}% | Stop: {STOP_THRESHOLD*100}%")
    print("=" * 60)

    try:
        while True:
            retention, debug, phase = calculate_retention_from_timestamp(p_factor, start_time)
            
            # 🆕 DISPLAY AS PERCENTAGE (0-100%)
            display_pct = min(100, retention * 100)  # Cap at 100%
            
            # Behavioral status
            if retention <= STOP_THRESHOLD:
                status, color = " RECONSTRUCTION", "\033[91m"
            elif retention < TRANSITION_THRESHOLD:
                status, color = " UNCERTAIN", "\033[93m"
            else:
                status, color = " CLEAR", "\033[92m"
            
            # Progress bar (0-100%)
            bar_len = 30
            filled = int(bar_len * (display_pct / 100))
            bar = "█" * filled + "░" * (bar_len - filled)
            
            # 🆕 FIXED OUTPUT
            output = (
                f"\r\033[K"  # Clear line
                f"Day {debug['game_days']:.2f} | "
                f"R={display_pct:5.1f}% [{bar}] | "
                f"Phase: {phase} | "
                f"Raw R={retention:.3f} | "
                f"{color}{status}\033[0m"
            )
            sys.stdout.write(output)
            sys.stdout.flush()
            
            # STOP CONDITION
            if retention <= STOP_THRESHOLD:
                print(f"\n\n STOPPED: R={retention:.3f} ({display_pct:.1f}%)")
                # print(" Parks & Yonelinas (2009): Unreliable recall")
                break
                
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n  Monitor stopped by user.")

if __name__ == "__main__":
    client = MongoClient("mongodb://localhost:27017")
    db = client["bigfive"]
    latest = db["ocean_scores"].find_one(sort=[("saved_at", -1)])
    
    if latest:
        start_monitor(latest['report_id'])
    else:
        print(" No candidates in database.")
