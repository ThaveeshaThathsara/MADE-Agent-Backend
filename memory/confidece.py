import random

def calculate_confidence(retention):
    
    print(f"Confidence calculation triggered for Retention: {retention}")
    
    # Random variation between -0.15 and +0.15
    variation = random.uniform(-0.15, 0.15)
    confidence = retention + variation
    
    # Clamp confidence between 0.0 and 1.0
    confidence = max(0.0, min(1.0, confidence))
    
    # Determine confidence band
    if confidence >= 0.8:
        label = "High Confidence"
    elif confidence >= 0.6:
        label = "Medium Confidence"
    elif confidence >= 0.4:
        label = "Low Confidence"
    elif confidence >= 0.3:
        label = "Very Low Confidence"
    else:
        label = "Confused"
        
    return round(confidence, 4), label
