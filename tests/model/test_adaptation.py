"""Tests for adaptive interest weight updates."""

import pytest
from src.model.adaptation import update_interest_weights, get_category_weight


class TestUpdateInterestWeights:
    """Test adaptive interest weight updates."""
    
    def test_view_event_increases_weight(self):
        """View event should increase weight by +0.08."""
        weights = {"electronics": 0.5}
        updated = update_interest_weights(weights, "electronics", 0.08)
        
        # After decay (0.5 * 0.9 = 0.45) + impact (0.08) = 0.53
        assert updated["electronics"] > 0.5
    
    def test_click_event_increases_weight(self):
        """Click event should increase weight by +0.30."""
        weights = {"electronics": 0.5}
        updated = update_interest_weights(weights, "electronics", 0.30)
        
        # After decay (0.5 * 0.9 = 0.45) + impact (0.30) = 0.75
        assert updated["electronics"] > 0.7
    
    def test_join_event_increases_weight(self):
        """Join event should increase weight by +0.60."""
        weights = {"electronics": 0.5}
        updated = update_interest_weights(weights, "electronics", 0.60)
        
        # After decay (0.5 * 0.9 = 0.45) + impact (0.60) = 1.0 (clamped)
        assert updated["electronics"] == 1.0
    
    def test_share_event_increases_weight(self):
        """Share event should increase weight by +0.20."""
        weights = {"electronics": 0.5}
        updated = update_interest_weights(weights, "electronics", 0.20)
        
        # After decay (0.5 * 0.9 = 0.45) + impact (0.20) = 0.65
        assert updated["electronics"] > 0.6
    
    def test_two_clicks_increase_recommendations(self):
        """Two clicks on electronics should increase electronics recommendations."""
        weights = {"electronics": 0.5, "home": 0.3}
        
        # First click
        weights = update_interest_weights(weights, "electronics", 0.30)
        first_electronics = weights["electronics"]
        
        # Second click
        weights = update_interest_weights(weights, "electronics", 0.30)
        second_electronics = weights["electronics"]
        
        # Electronics weight should increase after two clicks
        assert second_electronics > first_electronics
        assert second_electronics > weights.get("home", 0)
    
    def test_weights_clamped_to_one(self):
        """Weights should be clamped to maximum 1.0."""
        weights = {"electronics": 0.9}
        updated = update_interest_weights(weights, "electronics", 0.60)
        
        assert updated["electronics"] <= 1.0
    
    def test_weights_clamped_to_zero(self):
        """Weights should be clamped to minimum 0.0."""
        weights = {"electronics": 0.01}
        # Apply decay only (no new impact)
        updated = update_interest_weights(weights, "other", 0.0)
        
        assert updated["electronics"] >= 0.0
    
    def test_new_category_added(self):
        """New category should be added to weights."""
        weights = {"electronics": 0.5}
        updated = update_interest_weights(weights, "fashion", 0.30)
        
        assert "fashion" in updated
        assert updated["fashion"] == 0.30
    
    def test_decay_applied_to_existing_weights(self):
        """Decay should be applied to all existing weights."""
        weights = {"electronics": 0.8, "home": 0.6}
        updated = update_interest_weights(weights, "fashion", 0.0)
        
        # Both should decay by 10%
        assert updated["electronics"] < 0.8
        assert updated["home"] < 0.6


class TestGetCategoryWeight:
    """Test category weight retrieval."""
    
    def test_returns_existing_weight(self):
        weights = {"electronics": 0.7}
        assert get_category_weight(weights, "electronics") == 0.7
    
    def test_returns_default_for_missing(self):
        weights = {"electronics": 0.7}
        assert get_category_weight(weights, "fashion") == 0.3  # Default
    
    def test_custom_default(self):
        weights = {"electronics": 0.7}
        assert get_category_weight(weights, "fashion", default=0.5) == 0.5
