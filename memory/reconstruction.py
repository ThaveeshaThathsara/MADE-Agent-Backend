import random

def reconstruct_memory(retention):
   
    print(f"Memory reconstruction triggered for Retention: {retention}")
    
    variation = random.uniform(-0.15, 0.15)
    reconstruction = retention + variation
    
    # Clamp reconstruction between 0.0 and 1.0
    reconstruction = max(0.0, min(1.0, reconstruction))
    
    # Determine reconstruction band
    if reconstruction >= 0.8:
        label = "High Reconstruction"
    elif reconstruction >= 0.6:
        label = "Medium Reconstruction"
    elif reconstruction >= 0.4:
        label = "Low Reconstruction"
    elif reconstruction >= 0.3:
        label = "Very Low Reconstruction"
    else:
        label = "Confused"
        
    return round(reconstruction, 4), label