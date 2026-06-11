"""
Adaptive interest weight updates based on user events.

Two clicks on electronics should increase electronics recommendations.
"""

from typing import Dict, Any


def update_interest_weights(
    current_weights: Dict[str, float],
    category: str,
    impact: float
) -> Dict[str, float]:
    """
    Update user interest weights based on an event.
    
    Event impacts:
    - view: +0.08
    - click: +0.30
    - join: +0.60
    - share: +0.20
    
    Also applies slight decay to existing weights to prevent unbounded growth.
    Clamps weights to reasonable range [0.0, 1.0].
    
    Args:
        current_weights: Current interest weights dict {category: weight}
        category: Category of the product involved in the event
        impact: Impact value based on event type
    
    Returns:
        Updated interest weights dict
    """
    # Create a copy to avoid mutating original
    updated = dict(current_weights)
    
    # Apply decay to all existing weights (10% decay)
    # This prevents unbounded growth and allows interests to fade over time
    for cat in updated:
        updated[cat] = updated[cat] * 0.90
    
    # Add or update the category weight
    if category in updated:
        updated[category] += impact
    else:
        updated[category] = impact
    
    # Clamp all weights to [0.0, 1.0]
    for cat in updated:
        updated[cat] = max(0.0, min(1.0, updated[cat]))
    
    return updated


def get_category_weight(weights: Dict[str, float], category: str, default: float = 0.3) -> float:
    """
    Get the weight for a specific category with a default fallback.
    
    Args:
        weights: Interest weights dict
        category: Category to look up
        default: Default weight if category not found
    
    Returns:
        Weight value or default
    """
    return weights.get(category, default)
