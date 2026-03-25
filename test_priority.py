# import unittest
# from memory.priority import calculate_priority

# class TestPriorityLogic(unittest.TestCase):
#     def test_calculate_priority_normal(self):
#         # Kk = 0.8, TRk = 2.0, TAk = 5.0
#         # Vk = 0.8 * (2.0 / 5.0) = 0.8 * 0.4 = 0.32
#         prio, msg = calculate_priority(0.8, 2.0, 5.0)
#         self.assertAlmostEqual(prio, 0.32, places=4)
#         self.assertIn("Priority Vk: 0.32", msg)

#     def test_calculate_priority_urgent(self):
#         # High urgency: TRk = 4.0, TAk = 4.1
#         # Vk = 1.0 * (4.0/4.1) approx 0.975
#         prio, msg = calculate_priority(1.0, 4.0, 4.1)
#         self.assertTrue(prio > 0.9)
#         self.assertTrue(prio < 1.0)

#     def test_calculate_priority_expired(self):
#         # Expired: TAk = 0
#         prio, msg = calculate_priority(0.8, 2.0, 0.0)
#         self.assertEqual(prio, 10.0)
#         self.assertIn("Critical", msg)

# if __name__ == '__main__':
#     unittest.main()

"""
Priority-Based Memory Degradation System for MADE

Combines:
1. Ebbinghaus forgetting curve (Murre & Dros, 2015)
2. Personality modulation (Sutin et al., 2022)
3. Priority-based retention (Myers et al., 2017; Poth, 2020)

Mathematical Foundation:
R(t) = e^(-t / (S × P × V_k))

Where:
- R(t) = Retention at time t
- S = Base stability (Ebbinghaus parameter)
- P = Personality factor (OCEAN-based)
- V_k = Priority multiplier (importance-based)
- t = Time elapsed
"""

import math

def calculate_priority_multiplier(importance: float, alpha: float = 0.5) -> float:
    """
    Calculate priority multiplier for memory retention.
    
    Based on working memory prioritization research (Myers et al., 2017; Poth, 2020):
    - High importance tasks receive more attention → better encoding → slower forgetting
    - Low importance tasks receive less attention → weaker encoding → faster forgetting
    
    Formula: V_k = 1 + (K_k - 0.5) × α
    
    Args:
        importance (float): Task importance (0.0-1.0 scale)
            - 1.0 = Critical/High priority
            - 0.5 = Medium priority (neutral)
            - 0.0 = Low priority
        alpha (float): Scaling factor (default 0.5)
            - Controls how much priority affects memory
            - Typical range: 0.3-0.7
            - Higher alpha = stronger priority effects
    
    Returns:
        float: Priority multiplier (typically 0.75-1.25 range)
            - >1.0 = Remember longer (high priority)
            - =1.0 = Normal retention (medium priority)
            - <1.0 = Forget faster (low priority)
    
    Research Foundation:
        Myers et al. (2017): Attention crucial for working memory prioritization
        Poth (2020): Prioritization affects specific memory processes
        Lloyd & Gardelle (2021): Confidence affects response prioritization
    """
    # Clamp importance to valid range
    importance = max(0.0, min(1.0, importance))
    
    # Calculate multiplier
    # Center at 0.5 so medium priority (0.5) = neutral (1.0)
    V_k = 1.0 + (importance - 0.5) * alpha
    
    # Clamp to reasonable range (0.5-1.5)
    return max(0.5, min(1.5, V_k))


def calculate_urgency_factor(time_remaining: float, time_required: float) -> dict:
    """
    Calculate urgency factor based on deadline proximity.
    This is SEPARATE from memory retention - used for task scheduling.
    
    Based on Alister et al. (2024) goal prioritization formula:
    U_k = TR_k(t) / TA_k(t)
    
    Args:
        time_remaining (float): Time available before deadline (hours/days)
        time_required (float): Time needed to complete task (hours/days)
    
    Returns:
        dict: Urgency analysis with scheduling priority
    """
    if time_remaining <= 0:
        return {
            'urgency': float('inf'),
            'status': 'OVERDUE',
            'priority_level': 'CRITICAL',
            'message': '⚠️ Task is past deadline!'
        }
    
    if time_required <= 0:
        return {
            'urgency': 0.0,
            'status': 'COMPLETED',
            'priority_level': 'NONE',
            'message': '✓ No time required - task may be complete'
        }
    
    # Calculate urgency ratio
    urgency_ratio = time_required / time_remaining
    
    # Determine priority level
    if urgency_ratio >= 0.9:
        status = 'URGENT'
        priority_level = 'HIGH'
        message = f'⚠️ Urgent! Need {time_required:.1f} units, have {time_remaining:.1f}'
    elif urgency_ratio >= 0.5:
        status = 'MODERATE'
        priority_level = 'MEDIUM'
        message = f'→ Moderate urgency: {urgency_ratio*100:.0f}% of time needed'
    else:
        status = 'COMFORTABLE'
        priority_level = 'LOW'
        message = f'✓ Comfortable: {time_remaining/time_required:.1f}x time available'
    
    return {
        'urgency': urgency_ratio,
        'status': status,
        'priority_level': priority_level,
        'message': message,
        'time_remaining': time_remaining,
        'time_required': time_required
    }


def calculate_retention_with_priority(
    base_stability: float,
    p_factor: float,
    importance: float,
    time_elapsed: float,
    alpha: float = 0.5
) -> dict:
    """
    Calculate memory retention with personality AND priority modulation.
    
    Complete formula:
    R(t) = e^(-t / (S × P × V_k))
    
    Args:
        base_stability (float): Base Ebbinghaus stability (seconds/days)
        p_factor (float): Personality factor (from OCEAN scores)
        importance (float): Task importance (0.0-1.0)
        time_elapsed (float): Time since encoding (same units as stability)
        alpha (float): Priority effect strength (default 0.5)
    
    Returns:
        dict: Retention analysis with all factors
    """
    # Calculate priority multiplier
    V_k = calculate_priority_multiplier(importance, alpha)
    
    # Calculate effective stability
    # High priority → higher stability → slower forgetting
    effective_stability = base_stability * p_factor * V_k
    
    # Calculate retention using Ebbinghaus formula
    if effective_stability <= 0:
        retention = 0.0
    else:
        retention = math.exp(-time_elapsed / effective_stability)
    
    # Determine memory state
    if retention >= 0.7:
        memory_state = "STRONG"
        confidence = "High"
    elif retention >= 0.4:
        memory_state = "MODERATE"
        confidence = "Medium"
    elif retention >= 0.2:
        memory_state = "WEAK"
        confidence = "Low"
    else:
        memory_state = "CRITICAL"
        confidence = "Very Low - Reconstruction Needed"
    
    return {
        'retention': round(retention, 4),
        'memory_state': memory_state,
        'confidence': confidence,
        'factors': {
            'base_stability': base_stability,
            'p_factor': p_factor,
            'priority_multiplier': round(V_k, 4),
            'effective_stability': round(effective_stability, 2)
        },
        'time_elapsed': time_elapsed,
        'importance': importance
    }


def compare_priority_effects(
    base_stability: float,
    p_factor: float,
    time_elapsed: float,
    alpha: float = 0.5
) -> dict:
    """
    Compare retention across different priority levels.
    Demonstrates how priority affects memory degradation.
    
    Args:
        base_stability: Base memory stability
        p_factor: Personality factor
        time_elapsed: Time since encoding
        alpha: Priority effect strength
    
    Returns:
        dict: Comparison of retention at different priority levels
    """
    priorities = {
        'Critical (1.0)': 1.0,
        'High (0.8)': 0.8,
        'Medium (0.5)': 0.5,
        'Low (0.3)': 0.3,
        'Minimal (0.1)': 0.1
    }
    
    results = {}
    for label, importance in priorities.items():
        result = calculate_retention_with_priority(
            base_stability, p_factor, importance, time_elapsed, alpha
        )
        results[label] = result
    
    return results


# Example usage and validation
if __name__ == "__main__":
    print("="*70)
    print("PRIORITY-BASED MEMORY DEGRADATION SYSTEM")
    print("Research Foundation: Myers et al. (2017), Poth (2020), Sutin et al. (2022)")
    print("="*70)
    
    # Example parameters
    base_stability = 300  # 5 minutes base stability
    p_factor = 1.15       # Slightly above-average memory (good personality)
    time_elapsed = 180    # 3 minutes have passed
    
    print(f"\nScenario: Task after 3 minutes (base stability: 5 min, P-factor: {p_factor})")
    print("-"*70)
    
    # Compare different priority levels
    comparison = compare_priority_effects(base_stability, p_factor, time_elapsed)
    
    for label, result in comparison.items():
        print(f"\n{label}:")
        print(f"  Retention: {result['retention']*100:.1f}%")
        print(f"  Memory State: {result['memory_state']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Effective Stability: {result['factors']['effective_stability']:.1f}s")
    
    print("\n" + "="*70)
    print("URGENCY CALCULATION (Separate from Memory - for Task Scheduling)")
    print("="*70)
    
    # Example urgency calculations
    scenarios = [
        ("Comfortable deadline", 10.0, 30.0),
        ("Moderate urgency", 8.0, 10.0),
        ("High urgency", 9.0, 10.0),
        ("Overdue", 5.0, 0.0)
    ]
    
    for desc, time_req, time_avail in scenarios:
        urgency = calculate_urgency_factor(time_avail, time_req)
        print(f"\n{desc}:")
        print(f"  {urgency['message']}")
        print(f"  Priority Level: {urgency['priority_level']}")


        