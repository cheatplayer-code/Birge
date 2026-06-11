"""FastAPI router for ML/recommendation API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from .schemas import (
    EventRequest,
    RecommendationsResponse,
    TrustScoreResponse,
    HealthResponse,
    ModelInfoResponse,
    ModelInfo,
    RecommendationItem,
    ScoreComponents,
    ProductInfo,
    DealInfo,
)
from ..model.scoring import rank_deals_for_user, calculate_trust_score
from ..model.adaptation import update_interest_weights
from ..config import get_settings
from ..db.supabase_client import get_supabase_client, is_supabase_available
from ..model.embeddings import get_demo_data

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check service health status."""
    settings = get_settings()
    supabase_ok = await is_supabase_available()
    
    return HealthResponse(
        status="healthy",
        version="hackathon-v1",
        demo_mode=settings.is_demo_mode or not supabase_ok,
        supabase_connected=supabase_ok
    )


@router.get("/model-info", response_model=ModelInfoResponse)
async def model_info():
    """Return model transparency information."""
    return ModelInfoResponse(
        model_type="transparent_hybrid_ranking",
        version="hackathon-v1",
        formula="0.40 * interest_match + 0.20 * budget_fit + 0.20 * city_match + 0.20 * momentum",
        not_trained_ml=True,
        features=["interest_match", "budget_fit", "city_match", "momentum"]
    )


@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(user_id: str = Query(..., description="User UUID")):
    """Get personalized ranked deal recommendations for a user."""
    settings = get_settings()
    supabase_available = await is_supabase_available()
    
    # Use demo data if Supabase unavailable or in demo mode
    if not supabase_available or settings.is_demo_mode:
        logger.info(f"Using demo data for user {user_id}")
        demo_data = get_demo_data()
        user = demo_data.get("users", {}).get(user_id)
        deals = demo_data.get("deals", [])
        products = demo_data.get("products", {})
        
        if not user:
            # Create default demo user if not found
            user = {
                "id": user_id,
                "budget_tier": "mid",
                "city": "Алматы",
                "interests": ["electronics", "home"],
                "interest_weights": {"electronics": 0.5, "home": 0.3}
            }
        
        recommendations = rank_deals_for_user(user, deals, products)
    else:
        # Fetch from Supabase
        try:
            client = get_supabase_client()
            
            # Get user
            user_response = client.table("users").select("*").eq("id", user_id).execute()
            if not user_response.data:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            user = user_response.data[0]
            
            # Get deals with products
            deals_response = client.table("deals").select("""
                *,
                products (
                    id, name_ru, name_kk, category, tags,
                    retail_price_kzt, group_price_kzt, image_url
                )
            """).eq("status", "active").execute()
            
            deals = deals_response.data
            products = {d["products"]["id"]: d["products"] for d in deals if d.get("products")}
            
            recommendations = rank_deals_for_user(user, deals, products)
            
        except Exception as e:
            logger.error(f"Error fetching recommendations: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch recommendations")
    
    # Build response items
    recommendation_items = []
    for rec in recommendations:
        item = RecommendationItem(
            deal_id=rec["deal_id"],
            product_id=rec["product_id"],
            score=round(rec["score"], 3),
            components=ScoreComponents(
                interest_match=round(rec["components"]["interest_match"], 3),
                budget_fit=round(rec["components"]["budget_fit"], 3),
                city_match=round(rec["components"]["city_match"], 3),
                momentum=round(rec["components"]["momentum"], 3)
            ),
            why=rec["why"],
            product=ProductInfo(
                name_ru=rec["product"]["name_ru"],
                name_kk=rec["product"]["name_kk"],
                category=rec["product"]["category"],
                tags=rec["product"].get("tags", []),
                retail_price_kzt=rec["product"]["retail_price_kzt"],
                group_price_kzt=rec["product"]["group_price_kzt"],
                image_url=rec["product"].get("image_url")
            ),
            deal=DealInfo(
                city=rec["deal"]["city"],
                current_participants=rec["deal"]["current_participants"],
                target_participants=rec["deal"]["target_participants"],
                deadline=rec["deal"].get("deadline"),
                tiers=rec["deal"].get("tiers", [])
            )
        )
        recommendation_items.append(item)
    
    return RecommendationsResponse(
        success=True,
        user_id=user_id,
        recommendations=recommendation_items,
        model_info=ModelInfo(
            model_type="transparent_hybrid_ranking",
            version="hackathon-v1",
            not_trained_ml=True
        )
    )


@router.post("/events")
async def log_event(event: EventRequest):
    """Log user interaction event and update interest weights."""
    settings = get_settings()
    supabase_available = await is_supabase_available()
    
    # Update interest weights based on event
    event_impact = {
        "view": 0.08,
        "click": 0.30,
        "join": 0.60,
        "share": 0.20
    }
    
    impact = event_impact.get(event.event_type.value, 0.0)
    
    if not supabase_available or settings.is_demo_mode:
        # In demo mode, just return success
        logger.info(f"Demo event logged: {event.event_type.value} by {event.user_id} on {event.category}")
        return {
            "success": True,
            "message": f"Event {event.event_type.value} logged (demo mode)",
            "weight_update": {
                "category": event.category,
                "impact": impact
            }
        }
    
    try:
        client = get_supabase_client()
        
        # Insert event
        event_data = {
            "user_id": event.user_id,
            "event_type": event.event_type.value,
            "product_id": event.product_id,
            "deal_id": event.deal_id,
            "category": event.category,
            "metadata": event.metadata
        }
        client.table("events").insert(event_data).execute()
        
        # Update user interest weights
        if event.category:
            user_response = client.table("users").select("interest_weights").eq("id", event.user_id).execute()
            
            if user_response.data:
                current_weights = user_response.data[0].get("interest_weights", {}) or {}
                updated_weights = update_interest_weights(current_weights, event.category, impact)
                
                client.table("users").update({"interest_weights": updated_weights}).eq("id", event.user_id).execute()
        
        return {
            "success": True,
            "message": f"Event {event.event_type.value} logged successfully",
            "weight_update": {
                "category": event.category,
                "impact": impact
            }
        }
        
    except Exception as e:
        logger.error(f"Error logging event: {e}")
        raise HTTPException(status_code=500, detail="Failed to log event")


@router.get("/trust-score", response_model=TrustScoreResponse)
async def get_trust_score(user_id: str = Query(..., description="User UUID")):
    """Get rule-based trust score for a user."""
    settings = get_settings()
    supabase_available = await is_supabase_available()
    
    if not supabase_available or settings.is_demo_mode:
        # Demo trust score
        demo_data = get_demo_data()
        user = demo_data.get("users", {}).get(user_id, {})
        
        trust_score, factors = calculate_trust_score(user, [], demo_data.get("events", []))
        
        return TrustScoreResponse(
            success=True,
            user_id=user_id,
            trust_score=trust_score,
            factors=factors
        )
    
    try:
        client = get_supabase_client()
        
        # Get user
        user_response = client.table("users").select("*").eq("id", user_id).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        user = user_response.data[0]
        
        # Get user events
        events_response = client.table("events").select("*").eq("user_id", user_id).execute()
        events = events_response.data or []
        
        # Get user deals
        deals_response = client.table("deal_members").select("*, deals(status)").eq("user_id", user_id).execute()
        user_deals = deals_response.data or []
        
        trust_score, factors = calculate_trust_score(user, user_deals, events)
        
        return TrustScoreResponse(
            success=True,
            user_id=user_id,
            trust_score=trust_score,
            factors=factors
        )
        
    except Exception as e:
        logger.error(f"Error calculating trust score: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate trust score")
