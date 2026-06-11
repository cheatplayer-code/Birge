"""Rule-based trust score calculation (not trained ML)."""

from typing import Dict, Any, List


def calculate_trust_score(
    user: Dict[str, Any],
    user_deals: List[Dict[str, Any]],
    events: List[Dict[str, Any]]
) -> tuple:
    """
    Calculate rule-based trust score for a user.
    
    This is NOT trained ML - it's a transparent rule-based system.
    
    Factors:
    - SIM verified (if available): +20
    - Completed deals: +10 per deal (max 30)
    - Account age: +10 if > 30 days
    - Event diversity (view, click, join, share): +10
    - Rapid join penalty: -10 if joined many deals in short time
    
    Returns (trust_score, factors_dict) with score clamped 0-100.
    """
    from datetime import datetime
    
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
