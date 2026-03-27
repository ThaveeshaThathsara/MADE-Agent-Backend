def calculate_urgency(importance_kk, required_time_trk, available_time_tak):
    
    print(f"Urgency calculation triggered: Kk={importance_kk}, TRk={required_time_trk}, TAk={available_time_tak}")
    
    if available_time_tak <= 0:
        urgency = 10.0
        return urgency, "Critical Urgency (Time Expired)"
        
    urgency = importance_kk * (required_time_trk / available_time_tak)
    return round(urgency, 4), f"Urgency Vk: {round(urgency, 4)}"


def calculate_priority(p_factor, urgency, retention):
   
    print(f"Priority calculation triggered: P={p_factor}, U={urgency}, R={retention}")
    
    # Empirically validated coefficients
    INTERCEPT = 0.824
    BETA_URGENCY = 0.475
    BETA_PFACTOR = -0.287
    BETA_RETENTION = -0.084
    
    s = INTERCEPT + (BETA_URGENCY * urgency) + (BETA_PFACTOR * p_factor) + (BETA_RETENTION * retention)
    s = round(s, 4)
    
    print(f"   S = {INTERCEPT} + ({BETA_URGENCY} × {urgency}) + ({BETA_PFACTOR} × {p_factor}) + ({BETA_RETENTION} × {retention})")
    print(f"   Priority Score S = {s}")
    
    return s, f"Priority S: {s}"


def get_memory_strength(priority_level):
    
    STRENGTH_MAP = {
        'HIGH': {
            's_fast': 2.50,   # Slow decay — NPC retains high-priority tasks longer
            's_slow': 6.00,
            'label': 'Strong Memory (Slow Decay)'
        },
        'MED': {
            's_fast': 1.47,   # Default — Yadav (2025) baseline
            's_slow': 4.07,
            'label': 'Normal Memory (Default Decay)'
        },
        'LOW': {
            's_fast': 0.80,   # Fast decay — NPC forgets low-priority tasks quickly
            's_slow': 2.00,
            'label': 'Weak Memory (Fast Decay)'
        }
    }
    
    strength = STRENGTH_MAP.get(priority_level, STRENGTH_MAP['MED'])
    
    print(f"Memory strength for [{priority_level}]: S_FAST={strength['s_fast']}, S_SLOW={strength['s_slow']} — {strength['label']}")
    
    return strength
