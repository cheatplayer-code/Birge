"""ML model types and data structures."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class User:
    """User data structure."""
    id: str
    budget_tier: str = "mid"  # low, mid, high
    city: str = ""
    interests: List[str] = field(default_factory=list)
    interest_weights: Dict[str, float] = field(default_factory=dict)


@dataclass
class Product:
    """Product data structure."""
    id: str
    name_ru: str
    name_kk: str
    description_ru: Optional[str] = None
    description_kk: Optional[str] = None
    category: str = ""
    tags: List[str] = field(default_factory=list)
    retail_price_kzt: int = 0
    group_price_kzt: int = 0
    original_price_usd: Optional[float] = None
    weight_kg: Optional[float] = None
    cargo_price_kzt: Optional[int] = None
    image_url: Optional[str] = None
    embedding: Optional[List[float]] = None


@dataclass
class Deal:
    """Deal data structure."""
    id: str
    product_id: str
    city: str
    current_participants: int = 0
    target_participants: int = 0
    tiers: List[Dict[str, Any]] = field(default_factory=list)
    deadline: Optional[str] = None
    status: str = "active"
    created_at: Optional[str] = None


@dataclass
class ScoreComponents:
    """Individual score components."""
    interest_match: float = 0.0
    budget_fit: float = 0.0
    city_match: float = 0.0
    momentum: float = 0.0


@dataclass
class Recommendation:
    """Single recommendation with score and explanations."""
    deal_id: str
    product_id: str
    score: float
    components: ScoreComponents
    why: List[str]
    product: Dict[str, Any]
    deal: Dict[str, Any]
