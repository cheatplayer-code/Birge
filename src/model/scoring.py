"""
Core scoring functions for deal ranking.

Implements the exact formula:
score = 0.40 * interest_match + 0.20 * budget_fit + 0.20 * city_match + 0.20 * momentum

All components are clamped between 0 and 1.
"""

from typing import Dict, Any, List, Optional
import math


def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


def calculate_interest_match(
    user: Dict[str, Any],
    product: Dict[str, Any],
    products: Optional[Dict[str, Dict[str, Any]]] = None
) -> float:
    """
    Calculate interest match score between user and product.
    
    If embeddings exist, use cosine similarity.
    If embeddings are missing, use category/tag overlap with interest weights.
    
    Returns a value between 0 and 1.
    """
    # Try embedding-based similarity first
    if product.get("embedding") and user.get("embedding"):
        from .embeddings import cosine_similarity
        similarity = cosine_similarity(user["embedding"], product["embedding"])
        # Normalize from [-1, 1] to [0, 1]
        return clamp((similarity + 1) / 2)
    
    # Fallback: category/tag overlap with interest weights
    user_interests = set(user.get("interests", []))
    user_weights = user.get("interest_weights", {})
    
    product_category = product.get("category", "")
    product_tags = set(product.get("tags", []))
    
    # Check category match
    category_match = 0.0
    if product_category in user_interests:
        # Boost by interest weight if available
        weight = user_weights.get(product_category, 0.5)
        category_match = 0.6 + (weight * 0.4)  # Base 0.6, up to 1.0 with high weight
    
    # Check tag overlap
    tag_matches = user_interests.intersection(product_tags)
    tag_score = 0.0
    if tag_matches:
        # Sum weights for matching tags
        total_weight = sum(user_weights.get(tag, 0.3) for tag in tag_matches)
        tag_score = min(1.0, total_weight / len(tag_matches))
    
    # Combine category and tag scores
    if category_match > 0 and tag_score > 0:
        # Weighted average: category more important
        score = 0.7 * category_match + 0.3 * tag_score
    elif category_match > 0:
        score = category_match
    elif tag_score > 0:
        score = tag_score * 0.8  # Slight penalty for tag-only match
    else:
        # No match: check if category is somewhat related
        score = 0.2  # Small base score for exploration
    
    return clamp(score)


def calculate_budget_fit(budget_tier: str, group_price_kzt: int) -> float:
    """
    Calculate how well a deal fits the user's budget tier.
    
    Budget tiers:
    - low: best for <= 10000 KZT, smooth decay above
    - mid: best for 10000-50000 KZT
    - high: accepts 50000+ but should not punish cheaper deals too hard
    
    Returns a value between 0 and 1.
    """
    if budget_tier == "low":
        if group_price_kzt <= 10000:
            return 1.0
        elif group_price_kzt <= 20000:
            # Smooth decay from 1.0 to 0.5
            return clamp(1.0 - (group_price_kzt - 10000) / 20000)
        else:
            # Further decay
            return clamp(0.5 - (group_price_kzt - 20000) / 60000, 0.0, 0.5)
    
    elif budget_tier == "mid":
        if 10000 <= group_price_kzt <= 50000:
            return 1.0
        elif group_price_kzt < 10000:
            # Slight penalty for very cheap items (might be low quality)
            return clamp(0.7 + (group_price_kzt / 10000) * 0.3)
        else:
            # Decay above 50000
            return clamp(1.0 - (group_price_kzt - 50000) / 100000, 0.0, 1.0)
    
    elif budget_tier == "high":
        if group_price_kzt >= 50000:
            return 1.0
        elif group_price_kzt >= 20000:
            # Accept mid-range with slight penalty
            return clamp(0.6 + (group_price_kzt - 20000) / 100000)
        else:
            # Cheap items less interesting for high budget users
            return clamp(0.4 + (group_price_kzt / 20000) * 0.2)
    
    else:
        # Unknown tier: neutral score
        return 0.5


def calculate_city_match(user_city: str, deal_city: str) -> float:
    """
    Calculate city match score.
    
    - 1.0 if same city
    - 0.35 if different but shippable (assume all cities shippable)
    - 0.0 only if missing/invalid
    
    Returns a value between 0 and 1.
    """
    if not user_city or not deal_city:
        return 0.0
    
    # Normalize city names for comparison
    user_city_normalized = user_city.strip().lower()
    deal_city_normalized = deal_city.strip().lower()
    
    if user_city_normalized == deal_city_normalized:
        return 1.0
    
    # Different city but assume shippable within Kazakhstan
    kazakhstan_cities = ["алматы", "астана", "шымкент", "караганда", "актобе", "тараз"]
    if user_city_normalized in kazakhstan_cities and deal_city_normalized in kazakhstan_cities:
        return 0.35
    
    # Unknown city combination
    return 0.2


def calculate_momentum(deal: Dict[str, Any]) -> float:
    """
    Calculate deal momentum dynamically.
    
    Based on:
    - current_participants / target_participants (progress)
    - Time until deadline (urgency)
    - Progress toward next tier/target
    - Rate of participant acquisition (if created_at available)
    
    Returns a value between 0 and 1.
    """
    current = deal.get("current_participants", 0)
    target = deal.get("target_participants", 1)
    created_at = deal.get("created_at")
    deadline = deal.get("deadline")
    
    if target <= 0:
        return 0.0
    
    # Progress component (0-0.6)
    progress = current / target
    progress_score = clamp(progress) * 0.6
    
    # Urgency component (0-0.25)
    urgency_score = 0.0
    if deadline:
        try:
            from datetime import datetime
            deadline_dt = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
            now = datetime.now(deadline_dt.tzinfo) if deadline_dt.tzinfo else datetime.now()
            days_left = (deadline_dt - now).total_seconds() / 86400
            
            if days_left <= 0:
                urgency_score = 0.0  # Expired
            elif days_left <= 1:
                urgency_score = 0.25  # Very urgent
            elif days_left <= 3:
                urgency_score = 0.20
            elif days_left <= 7:
                urgency_score = 0.15
            else:
                urgency_score = 0.10
        except Exception:
            urgency_score = 0.10  # Default if can't parse
    else:
        urgency_score = 0.10  # Default if no deadline
    
    # Velocity component (0-0.15)
    velocity_score = 0.0
    if created_at and current > 0:
        try:
            from datetime import datetime
            created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            now = datetime.now(created_dt.tzinfo) if created_dt.tzinfo else datetime.now()
            days_active = max(1, (now - created_dt).total_seconds() / 86400)
            participants_per_day = current / days_active
            
            # Good velocity: > 5 participants per day
            if participants_per_day >= 5:
                velocity_score = 0.15
            elif participants_per_day >= 2:
                velocity_score = 0.10
            elif participants_per_day >= 1:
                velocity_score = 0.07
            else:
                velocity_score = 0.03
        except Exception:
            velocity_score = 0.05  # Default if can't parse
    else:
        # No creation date but has participants: assume moderate velocity
        velocity_score = 0.05 if current > 0 else 0.0
    
    # Tier progress bonus (0-0.1)
    tiers = deal.get("tiers", [])
    tier_bonus = 0.0
    if tiers and current > 0:
        # Check if close to next tier threshold
        for tier in sorted(tiers, key=lambda t: t.get("min_participants", 0)):
            min_participants = tier.get("min_participants", 0)
            if current >= min_participants:
                tier_bonus = 0.05  # Already reached a tier
            elif current >= min_participants * 0.8:
                tier_bonus = 0.10  # Close to next tier (80% there)
                break
    
    total_momentum = progress_score + urgency_score + velocity_score + tier_bonus
    return clamp(total_momentum)


def calculate_final_score(components: Dict[str, float]) -> float:
    """
    Calculate final score using the exact formula.
    
    score = 0.40 * interest_match + 0.20 * budget_fit + 0.20 * city_match + 0.20 * momentum
    
    All components must already be clamped between 0 and 1.
    """
    interest_match = clamp(components.get("interest_match", 0.0))
    budget_fit = clamp(components.get("budget_fit", 0.0))
    city_match = clamp(components.get("city_match", 0.0))
    momentum = clamp(components.get("momentum", 0.0))
    
    score = (
        0.40 * interest_match +
        0.20 * budget_fit +
        0.20 * city_match +
        0.20 * momentum
    )
    
    return clamp(score)


def rank_deals_for_user(
    user: Dict[str, Any],
    deals: List[Dict[str, Any]],
    products: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Rank deals for a user based on the scoring formula.
    
    Returns a list of recommendations sorted by score (descending).
    Each recommendation includes score, components, and explanation chips.
    """
    from .explain import generate_explanation_chips
    
    recommendations = []
    
    for deal in deals:
        product_id = deal.get("product_id")
        product = products.get(product_id, {})
        
        if not product:
            continue
        
        # Calculate components
        interest_match = calculate_interest_match(user, product, products)
        budget_fit = calculate_budget_fit(
            user.get("budget_tier", "mid"),
            product.get("group_price_kzt", 0)
        )
        city_match = calculate_city_match(
            user.get("city", ""),
            deal.get("city", "")
        )
        momentum = calculate_momentum(deal)
        
        components = {
            "interest_match": interest_match,
            "budget_fit": budget_fit,
            "city_match": city_match,
            "momentum": momentum
        }
        
        # Calculate final score
        score = calculate_final_score(components)
        
        # Generate explanation chips
        why = generate_explanation_chips(
            components,
            product,
            deal,
            user.get("interest_weights", {})
        )
        
        recommendations.append({
            "deal_id": deal.get("id"),
            "product_id": product_id,
            "score": score,
            "components": components,
            "why": why,
            "product": product,
            "deal": deal
        })
    
    # Sort by score descending
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    
    return recommendations


def calculate_trust_score(
    user: Dict[str, Any],
    user_deals: List[Dict[str, Any]],
    events: List[Dict[str, Any]]
) -> tuple:
    """
    Calculate rule-based trust score for a user.
    
    Factors:
    - SIM verified (if available): +20
    - Completed deals: +10 per deal (max 30)
    - Account age: +10 if > 30 days
    - Event diversity (view, click, join, share): +10
    - Rapid join penalty: -10 if joined many deals in short time
    
    Returns (trust_score, factors_dict) with score clamped 0-100.
    """
    factors = {}
    score = 50  # Base score
    
    # SIM verification bonus (check metadata or profile)
    sim_verified = user.get("sim_verified", False) or user.get("metadata", {}).get("sim_verified", False)
    if sim_verified:
        score += 20
        factors["sim_verified"] = True
    else:
        factors["sim_verified"] = False
    
    # Completed deals bonus
    completed_deals = [d for d in user_deals if d.get("status") == "completed"]
    completed_count = min(len(completed_deals), 3)  # Max 3 counted
    completed_bonus = completed_count * 10
    score += completed_bonus
    factors["completed_deals"] = completed_count
    factors["completed_deals_bonus"] = completed_bonus
    
    # Account age bonus
    created_at = user.get("created_at")
    if created_at:
        try:
            from datetime import datetime
            created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            now = datetime.now(created_dt.tzinfo) if created_dt.tzinfo else datetime.now()
            days_old = (now - created_dt).total_seconds() / 86400
            if days_old > 30:
                score += 10
                factors["account_age_days"] = int(days_old)
                factors["account_age_bonus"] = True
            else:
                factors["account_age_days"] = int(days_old)
                factors["account_age_bonus"] = False
        except Exception:
            factors["account_age_bonus"] = False
    else:
        factors["account_age_bonus"] = False
    
    # Event diversity bonus
    event_types = set(e.get("event_type") for e in events)
    if len(event_types) >= 3:  # Has at least 3 different event types
        score += 10
        factors["event_diversity"] = True
    else:
        factors["event_diversity"] = False
    
    # Rapid join penalty
    join_events = [e for e in events if e.get("event_type") == "join"]
    if len(join_events) > 5:
        # Check if many joins in short time
        try:
            join_times = []
            for e in join_events:
                created = e.get("created_at")
                if created:
                    join_times.append(datetime.fromisoformat(created.replace("Z", "+00:00")))
            
            if len(join_times) >= 5:
                join_times.sort()
                # Check if 5+ joins in 24 hours
                time_span = (join_times[-1] - join_times[0]).total_seconds() / 3600
                if time_span <= 24:
                    score -= 10
                    factors["rapid_join_penalty"] = True
                else:
                    factors["rapid_join_penalty"] = False
            else:
                factors["rapid_join_penalty"] = False
        except Exception:
            factors["rapid_join_penalty"] = False
    else:
        factors["rapid_join_penalty"] = False
    
    # Clamp to 0-100
    final_score = max(0, min(100, score))
    factors["base_score"] = 50
    factors["final_score"] = final_score
    
    return final_score, factors
