import math

def calculate_p_factor(normalized_scores):

    O = normalized_scores.get('openness', 0.5)
    C = normalized_scores.get('conscientiousness', 0.5)
    E = normalized_scores.get('extraversion', 0.5)
    A = normalized_scores.get('agreeableness', 0.5)
    N = normalized_scores.get('neuroticism', 0.5)

    # Calculate P-factor using exact meta-analytic weights
    p_factor = 1.0 + (0.235 * O) + (0.229 * C) + (0.170 * E) + (0.076 * A) - (0.192 * N)

    return round(p_factor, 4)


def calculate_p_factor_with_breakdown(normalized_scores):
    
    O = normalized_scores.get('openness', 0.5)
    C = normalized_scores.get('conscientiousness', 0.5)
    E = normalized_scores.get('extraversion', 0.5)
    A = normalized_scores.get('agreeableness', 0.5)
    N = normalized_scores.get('neuroticism', 0.5)
    
    # Calculate individual contributions
    contributions = {
        'base': 1.0,
        'openness': 0.235 * O,
        'conscientiousness': 0.229 * C,
        'extraversion': 0.170 * E,
        'agreeableness': 0.076 * A,
        'neuroticism': -0.192 * N
    }
    
    # Calculate total
    p_factor = sum(contributions.values())
    clamped_p_factor = max(0.5, min(1.5, p_factor))
    
    return {
        'p_factor': round(clamped_p_factor, 4),
        'p_factor_unclamped': round(p_factor, 4),
        'contributions': {k: round(v, 4) for k, v in contributions.items()},
        'was_clamped': p_factor != clamped_p_factor
    }


if __name__ == "__main__":
    # Test the function
    print("="*60)
    print("Testing P-Factor Calculation (Sutin et al., 2022)")
    print("="*60)
    
    # Test case 1: Average personality (all 0.5)
    avg_person = {
        'openness': 0.5,
        'conscientiousness': 0.5,
        'extraversion': 0.5,
        'agreeableness': 0.5,
        'neuroticism': 0.5
    }
    print("\nTest 1: Average Personality (all 0.5)")
    print(f"P-Factor: {calculate_p_factor(avg_person)}")
    breakdown = calculate_p_factor_with_breakdown(avg_person)
    print(f"Breakdown: {breakdown}")
    
    # Test case 2: Optimal memory (high C, O, low N)
    optimal_person = {
        'openness': 0.85,
        'conscientiousness': 0.90,
        'extraversion': 0.5,
        'agreeableness': 0.5,
        'neuroticism': 0.20
    }
    print("\nTest 2: Optimal Memory Profile")
    print(f"P-Factor: {calculate_p_factor(optimal_person)}")
    breakdown = calculate_p_factor_with_breakdown(optimal_person)
    print(f"Breakdown: {breakdown}")
    
    # Test case 3: Poor memory (low C, high N)
    poor_person = {
        'openness': 0.30,
        'conscientiousness': 0.35,
        'extraversion': 0.5,
        'agreeableness': 0.5,
        'neuroticism': 0.65
    }
    print("\nTest 3: Poor Memory Profile")
    print(f"P-Factor: {calculate_p_factor(poor_person)}")
    breakdown = calculate_p_factor_with_breakdown(poor_person)
    print(f"Breakdown: {breakdown}")
    print("="*60)
    