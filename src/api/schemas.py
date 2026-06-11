"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Supported event types for user interaction tracking."""
    VIEW = "view"
    CLICK = "click"
    JOIN = "join"
    SHARE = "share"


class EventRequest(BaseModel):
    """Request schema for POST /events endpoint."""
    user_id: str = Field(..., description="User UUID")
    event_type: EventType = Field(..., description="Event type: view, click, join, share")
    product_id: Optional[str] = Field(None, description="Product UUID")
    deal_id: Optional[str] = Field(None, description="Deal UUID")
    category: Optional[str] = Field(None, description="Product category")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event metadata")


class ScoreComponents(BaseModel):
    """Individual score components for transparency."""
    interest_match: float = Field(..., ge=0.0, le=1.0, description="Interest match score (0-1)")
    budget_fit: float = Field(..., ge=0.0, le=1.0, description="Budget fit score (0-1)")
    city_match: float = Field(..., ge=0.0, le=1.0, description="City match score (0-1)")
    momentum: float = Field(..., ge=0.0, le=1.0, description="Momentum score (0-1)")


class ProductInfo(BaseModel):
    """Product information returned in recommendations."""
    name_ru: str = Field(..., description="Product name in Russian")
    name_kk: str = Field(..., description="Product name in Kazakh")
    category: str = Field(..., description="Product category")
    tags: List[str] = Field(default_factory=list, description="Product tags")
    retail_price_kzt: int = Field(..., description="Retail price in KZT")
    group_price_kzt: int = Field(..., description="Group buy price in KZT")
    image_url: Optional[str] = Field(None, description="Product image URL")


class DealInfo(BaseModel):
    """Deal information returned in recommendations."""
    city: str = Field(..., description="Deal city")
    current_participants: int = Field(..., description="Current number of participants")
    target_participants: int = Field(..., description="Target number of participants")
    deadline: Optional[datetime] = Field(None, description="Deal deadline")
    tiers: List[Dict[str, Any]] = Field(default_factory=list, description="Deal tiers")


class RecommendationItem(BaseModel):
    """Single recommendation item with score and explanations."""
    deal_id: str = Field(..., description="Deal UUID")
    product_id: str = Field(..., description="Product UUID")
    score: float = Field(..., ge=0.0, le=1.0, description="Final recommendation score (0-1)")
    components: ScoreComponents = Field(..., description="Score breakdown")
    why: List[str] = Field(default_factory=list, description="Explanation chips")
    product: ProductInfo = Field(..., description="Product details")
    deal: DealInfo = Field(..., description="Deal details")


class ModelInfo(BaseModel):
    """Model transparency information."""
    model_type: str = Field("transparent_hybrid_ranking", description="Model type identifier")
    version: str = Field("hackathon-v1", description="Model version")
    not_trained_ml: bool = Field(True, description="Indicates this is rule-based, not trained ML")


class RecommendationsResponse(BaseModel):
    """Response schema for GET /recommendations endpoint."""
    success: bool = Field(True, description="Request success status")
    user_id: str = Field(..., description="User UUID")
    recommendations: List[RecommendationItem] = Field(default_factory=list, description="Ranked recommendations")
    model_info: ModelInfo = Field(default_factory=ModelInfo, description="Model transparency info")


class TrustScoreResponse(BaseModel):
    """Response schema for GET /trust-score endpoint."""
    success: bool = Field(True, description="Request success status")
    user_id: str = Field(..., description="User UUID")
    trust_score: int = Field(..., ge=0, le=100, description="Trust score (0-100)")
    factors: Dict[str, Any] = Field(default_factory=dict, description="Score breakdown factors")


class HealthResponse(BaseModel):
    """Response schema for GET /health endpoint."""
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    demo_mode: bool = Field(..., description="Whether running in demo mode")
    supabase_connected: bool = Field(..., description="Whether Supabase is connected")


class ModelInfoResponse(BaseModel):
    """Response schema for GET /model-info endpoint."""
    model_type: str = Field("transparent_hybrid_ranking", description="Model type")
    version: str = Field("hackathon-v1", description="Model version")
    formula: str = Field(
        "0.40 * interest_match + 0.20 * budget_fit + 0.20 * city_match + 0.20 * momentum",
        description="Ranking formula"
    )
    not_trained_ml: bool = Field(True, description="Indicates this is rule-based, not trained ML")
    features: List[str] = Field(
        ["interest_match", "budget_fit", "city_match", "momentum"],
        description="Features used in ranking"
    )
