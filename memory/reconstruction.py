import random

def reconstruct_memory(retention):
    """
    Reconstruct memory with random variation.
    Formula: Reconstruction = Retention ± random(0, 0.15) (Weise et al., 2024)
    SD = 0.15 on 0-1 scale.
    
    Args:
        retention (float): The current memory retention level (0.0 to 1.0).
        
    Returns:
        float: Reconstructed memory score (0.0 to 1.0).
        str: Reconstruction label (High, Medium, Low, Very Low, Confused).
    """
    print(f"Memory reconstruction triggered for Retention: {retention}")
    
    # Random variation between -0.15 and +0.15
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