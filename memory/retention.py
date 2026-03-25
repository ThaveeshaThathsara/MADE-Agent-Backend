# """
# Memory Retention Calculation Module - Two-Phase Decay Model
# Uses Ebbinghaus forgetting curve enhanced with research-validated two-phase parameters.

# Model Phases:
# 1. Fast Decay (Neural Unbinding): S = 1.47 (Yadav 2025: Mean - 1SD)
# 2. Slow Decay (Trace Consolidation): S = 4.07 (Yadav 2025: Mean + 1SD)

# Transition: 
# Threshold at 40% (Kornell et al., 2011) triggers transition from Phase 1 to Phase 2.

# Behavioral Stop:
# Threshold at 30% (Parks & Yonelinas, 2009) marks the limit of functional retrieval.
# """

# import math
# import time
# import sys
# from datetime import datetime
# from pymongo import MongoClient

# # Research-Validated Constants
# S_FAST = 1.47  # Yadav (2025) Fast decay constant
# S_SLOW = 4.07  # Yadav (2025) Slow decay constant
# TRANSITION_THRESHOLD = 0.40  # Kornell et al. (2011)
# STOP_THRESHOLD = 0.30        # Parks & Yonelinas (2009)

# def calculate_retention(p_factor, days=0, strength=None, transition_info=None):
#     """
#     Calculate memory retention using the two-phase decay model.
#     """
#     p_factor = max(0.5, min(1.5, p_factor))
#     days = max(0, days)
    
#     # Phase 1: Fast Decay (until 40%)
#     # R(t) = P * e^(-t / S_fast)
#     r_fast = p_factor * math.exp(-days / S_FAST)
    
#     if r_fast >= TRANSITION_THRESHOLD:
#         return round(max(0.0, r_fast), 4), "Phase 1 (Fast)"
    
#     # Phase 2: Slow Decay (starts at 40%)
#     # R(t) = 0.40 * e^(- (t - t_transition) / S_slow)
#     # Finding t_transition for Phase 1: 0.40 = P * e^(-t_t / 1.47)
#     # -t_t / 1.47 = ln(0.40 / P)
#     # t_t = -1.47 * ln(0.40 / P)
#     t_transition = -S_FAST * math.log(TRANSITION_THRESHOLD / p_factor)
    
#     if days <= t_transition:
#         return round(r_fast, 4), "Phase 1 (Fast)"
        
#     t_in_slow = days - t_transition
#     r_slow = TRANSITION_THRESHOLD * math.exp(-t_in_slow / S_SLOW)
    
#     # Clamp to STOP_THRESHOLD (30%) as requested in previous instruction + current logic
#     final_r = max(STOP_THRESHOLD, r_slow)
    
#     return round(final_r, 4), "Phase 2 (Slow)"

# def calculate_retention_from_timestamp(p_factor, created_at, game_time_scale=60):
#     """
#     Calculate retention from real timestamps.
#     """
#     time_delta = datetime.now() - created_at
#     real_seconds = time_delta.total_seconds()
#     game_days = real_seconds / game_time_scale
    
#     retention, phase = calculate_retention(p_factor, game_days)
    
#     debug_info = {
#         "game_days": game_days,
#         "real_seconds": real_seconds,
#         "phase": phase
#     }
    
#     return retention, debug_info, phase

# def start_monitor(report_id):
#     client = MongoClient("mongodb://localhost:27017")
#     db = client["bigfive"]
#     collection = db["ocean_scores"]
#     candidate = collection.find_one({"report_id": report_id})

#     if not candidate:
#         print("Report ID not found!")
#         return

#     p_factor = candidate["p_factor"]
#     # For simulation monitor, we use saved_at if available, otherwise now
#     start_time_str = candidate.get("saved_at")
#     if start_time_str:
#         start_time = datetime.fromisoformat(start_time_str)
#     else:
#         start_time = datetime.now()

#     print(f"\n🚀 STARTING TWO-PHASE MONITOR | ID: {report_id}")
#     print(f"📈 P-Factor: {p_factor:.4f}")
#     print(f"🔬 S_Fast: {S_FAST} | S_Slow: {S_SLOW}")
#     print(f"⏱️  Transition: {TRANSITION_THRESHOLD*100}% | Stop: {STOP_THRESHOLD*100}%")
#     print(f"------------------------------------------------------------------\n")

#     try:
#         while True:
#             retention, debug, phase = calculate_retention_from_timestamp(p_factor, start_time)
            
#             # Behavioral Flags
#             recall_difficulty = retention < TRANSITION_THRESHOLD
#             reconstruction_req = retention <= STOP_THRESHOLD
            
#             # Status Mapping
#             if reconstruction_req:
#                 status = "RECONSTRUCTION REQUIRED"
#                 status_color = "\033[91m" # Red
#             elif recall_difficulty:
#                 status = "UNCERTAIN RECALL"
#                 status_color = "\033[93m" # Yellow
#             else:
#                 status = "CLEAR RECALL"
#                 status_color = "\033[92m" # Green
            
#             # Progress Bar
#             bar_len = 30
#             filled = int(bar_len * retention)
#             bar = "█" * filled + "-" * (bar_len - filled)
            
#             # Terminal Output
#             output = (
#                 f"\r\033[K" # Clear line
#                 f"Day {debug['game_days']:.2f} | "
#                 f"Ret: {retention*100:.2f}% [{bar}] | "
#                 f"Phase: {phase} | "
#                 f"Status: {status_color}{status}\033[0m"
#             )
#             sys.stdout.write(output)
#             sys.stdout.flush()

#             # Transition Time Recording (One-off)
#             if recall_difficulty and "transition_time" not in candidate:
#                 collection.update_one(
#                     {"report_id": report_id},
#                     {"$set": {"transition_time": datetime.now().isoformat()}}
#                 )
#                 candidate["transition_time"] = True # Flag locally to avoid re-update

#             # STOP TRIGGER
#             if reconstruction_req:
#                 print(f"\n\n� STOPPED: Retention hit {STOP_THRESHOLD*100}% threshold.")
#                 print(f"⚠️  Parks & Yonelinas (2009): Memory signal indistinguishable from noise.")
#                 break

#             time.sleep(0.5)
#     except KeyboardInterrupt:
#         print("\n\nMonitor stopped by user.")

# if __name__ == "__main__":
#     client = MongoClient("mongodb://localhost:27017")
#     db = client["bigfive"]
#     latest = db["ocean_scores"].find_one(sort=[("saved_at", -1)])
    
#     if latest:
#         start_monitor(latest['report_id'])
#     else:
#         print("No candidates found in database.")


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
    """
    FIXED: Proper 2-phase decay with correct transition.
    Accepts optional s_fast/s_slow for priority-based memory strength.
    Accepts **kwargs for backward compatibility (e.g. strength=2.8).
    """
    # Use priority-based S values if provided, otherwise use defaults
    s_f = s_fast if s_fast is not None else S_FAST
    s_s = s_slow if s_slow is not None else S_SLOW
    
    p_factor = max(0.5, min(1.5, p_factor))  # Clamp P: 50-150%
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
        print("❌ Report ID not found!")
        return

    p_factor = candidate["p_factor"]
    start_time = datetime.fromisoformat(candidate.get("saved_at", datetime.now(timezone.utc).isoformat()))

    print(f"\n🚀 TWO-PHASE MONITOR STARTED | ID: {report_id}")
    print(f"📈 P-Factor: {p_factor:.2f} ({p_factor*100:.0f}%)")
    print(f"🔬 S_FAST: {S_FAST:.2f} | S_SLOW: {S_SLOW:.2f}")
    print(f"🎯 Transition: {TRANSITION_THRESHOLD*100}% | Stop: {STOP_THRESHOLD*100}%")
    print("=" * 60)

    try:
        while True:
            retention, debug, phase = calculate_retention_from_timestamp(p_factor, start_time)
            
            # 🆕 DISPLAY AS PERCENTAGE (0-100%)
            display_pct = min(100, retention * 100)  # Cap at 100%
            
            # Behavioral status
            if retention <= STOP_THRESHOLD:
                status, color = "🛑 RECONSTRUCTION", "\033[91m"
            elif retention < TRANSITION_THRESHOLD:
                status, color = "⚠️ UNCERTAIN", "\033[93m"
            else:
                status, color = "✅ CLEAR", "\033[92m"
            
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
                print(f"\n\n🛑 STOPPED: R={retention:.3f} ({display_pct:.1f}%)")
                print("⚠️ Parks & Yonelinas (2009): Unreliable recall")
                break
                
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n⏹️ Monitor stopped by user.")

if __name__ == "__main__":
    client = MongoClient("mongodb://localhost:27017")
    db = client["bigfive"]
    latest = db["ocean_scores"].find_one(sort=[("saved_at", -1)])
    
    if latest:
        start_monitor(latest['report_id'])
    else:
        print("❌ No candidates in database.")
