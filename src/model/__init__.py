"""ML model module."""

from .scoring import (
    clamp,
    calculate_interest_match,
    calculate_budget_fit,
    calculate_city_match,
    calculate_momentum,
    calculate_final_score,
    rank_deals_for_user,
    calculate_trust_score,
)
from .explain import generate_explanation_chips
from .embeddings import cosine_similarity, get_deterministic_embedding, get_demo_data
from .adaptation import update_interest_weights

__all__ = [
    "clamp",
    "calculate_interest_match",
    "calculate_budget_fit",
    "calculate_city_match",
    "calculate_momentum",
    "calculate_final_score",
    "rank_deals_for_user",
    "calculate_trust_score",
    "generate_explanation_chips",
    "cosine_similarity",
    "get_deterministic_embedding",
    "get_demo_data",
    "update_interest_weights",
]
