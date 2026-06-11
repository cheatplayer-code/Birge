"""Explanation chip generation for recommendations."""

from typing import Dict, Any, List


def generate_explanation_chips(
    components: Dict[str, float],
    product: Dict[str, Any],
    deal: Dict[str, Any],
    interest_weights: Dict[str, float]
) -> List[str]:
    """
    Generate explanation chips based on top score components.
    
    Chips are generated dynamically from score components, not hardcoded.
    
    Examples:
    - "электроника" (from category match)
    - "Алматы" (from city match)
    - "в бюджете" (from budget fit)
    - "быстро набирается" (from momentum)
    - "похоже на ваши клики" (from high interest weight)
    
    Returns a list of 2-4 explanation chips.
    """
    chips = []
    
    # Sort components by score to find top contributors
    sorted_components = sorted(
        components.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Interest match chip
    interest_score = components.get("interest_match", 0.0)
    if interest_score >= 0.6:
        category = product.get("category", "")
        
        # Check if this category has high user weight (indicating clicks)
        user_weight = interest_weights.get(category, 0.0)
        if user_weight >= 0.5:
            # High weight indicates previous clicks/interest
            chips.append("похоже на ваши клики")
        elif category:
            # Just category match
            chips.append(category)
    
    # City match chip
    city_score = components.get("city_match", 0.0)
    if city_score >= 0.9:
        deal_city = deal.get("city", "")
        if deal_city:
            chips.append(deal_city)
    elif city_score >= 0.3:
        # Different but shippable city
        chips.append("доставка возможна")
    
    # Budget fit chip
    budget_score = components.get("budget_fit", 0.0)
    if budget_score >= 0.8:
        chips.append("в бюджете")
    elif budget_score >= 0.5:
        chips.append("доступная цена")
    
    # Momentum chip
    momentum_score = components.get("momentum", 0.0)
    if momentum_score >= 0.7:
        current = deal.get("current_participants", 0)
        target = deal.get("target_participants", 1)
        progress = current / target if target > 0 else 0
        
        if progress >= 0.8:
            chips.append("почти собрано")
        elif progress >= 0.5:
            chips.append("быстро набирается")
        else:
            chips.append("набирает участников")
    elif momentum_score >= 0.4:
        chips.append("активный набор")
    
    # Ensure we have at least 2 chips
    if len(chips) < 2:
        # Add generic positive chips based on available data
        if product.get("category") and "похоже на ваши клики" not in chips:
            if len(chips) < 2:
                chips.append(product.get("category"))
        
        if len(chips) < 2:
            chips.append("рекомендуем")
    
    # Limit to 4 chips maximum
    return chips[:4]
