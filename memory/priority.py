def calculate_urgency(importance_kk, required_time_trk, available_time_tak):
    """
    Calculate task urgency perception using Alister et al. (2024) formula:
    Vk(t) = Kk * TRk(t) / TAk(t)
    
    Args:
        importance_kk (float): Subjective importance of the goal (0.0 to 1.0).
        required_time_trk (float): Time required to achieve the goal.
        available_time_tak (float): Time available to achieve the goal.
        
    Returns:
        float: Urgency value Vk(t).
        str: Description/Log.
    """
    print(f"Urgency calculation triggered: Kk={importance_kk}, TRk={required_time_trk}, TAk={available_time_tak}")
    
    if available_time_tak <= 0:
        urgency = 10.0
        return urgency, "Critical Urgency (Time Expired)"
        
    urgency = importance_kk * (required_time_trk / available_time_tak)
    return round(urgency, 4), f"Urgency Vk: {round(urgency, 4)}"


def calculate_priority(p_factor, urgency, retention):
    """
    Calculate task priority using empirically validated regression model.
    
    Formula: S = 0.824 + (0.475 × U) - (0.287 × P) - (0.084 × R)
    
    Where:
        S  = Priority score (higher = more prioritized)
        U  = Urgency perception score (0.0 to 1.0)
        P  = P-Factor from OCEAN personality model (0.5 to 1.5)
        R  = Ebbinghaus memory retention score (0.0 to 1.0)
    
    Args:
        p_factor (float): Personality factor from OCEAN model (0.5 to 1.5).
        urgency (float): Urgency perception score (0.0 to 1.0).
        retention (float): Ebbinghaus memory retention score (0.0 to 1.0).
        
    Returns:
        float: Priority score S.
        str: Description/Log.
    """
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
    """
    Map task priority level to memory strength parameters (S_FAST, S_SLOW)
    for the 2-phase Ebbinghaus retention model.
    
    Higher S values = slower decay = NPC remembers longer.
    Lower S values  = faster decay = NPC forgets quicker.
    
    The 40% transition threshold remains constant across all levels.
    
    Args:
        priority_level (str): 'HIGH', 'MED', or 'LOW'
        
    Returns:
        dict: { s_fast, s_slow, label }
    """
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
