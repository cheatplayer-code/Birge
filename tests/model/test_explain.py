"""Tests for explanation chip generation."""

import pytest
from src.model.explain import generate_explanation_chips


class TestGenerateExplanationChips:
    """Test explanation chip generation."""
    
    def test_city_chip_for_same_city(self):
        """Should generate city chip when city matches."""
        components = {"interest_match": 0.5, "budget_fit": 0.5, "city_match": 1.0, "momentum": 0.5}
        product = {"category": "electronics"}
        deal = {"city": "Алматы"}
        
        chips = generate_explanation_chips(components, product, deal, {})
        
        assert "Алматы" in chips
    
    def test_budget_chip_for_good_fit(self):
        """Should generate 'в бюджете' chip when budget fit is high."""
        components = {"interest_match": 0.5, "budget_fit": 0.9, "city_match": 0.5, "momentum": 0.5}
        product = {"category": "electronics"}
        deal = {"city": "Алматы"}
        
        chips = generate_explanation_chips(components, product, deal, {})
        
        assert "в бюджете" in chips
    
    def test_momentum_chip_for_high_progress(self):
        """Should generate momentum chip when progress is high."""
        components = {"interest_match": 0.5, "budget_fit": 0.5, "city_match": 0.5, "momentum": 0.8}
        product = {"category": "electronics"}
        deal = {"city": "Алматы", "current_participants": 18, "target_participants": 20}
        
        chips = generate_explanation_chips(components, product, deal, {})
        
        # Should have some momentum-related chip
        momentum_chips = ["почти собрано", "быстро набирается", "набирает участников", "активный набор"]
        assert any(chip in chips for chip in momentum_chips)
    
    def test_clicks_chip_for_high_weight(self):
        """Should generate 'похоже на ваши клики' when category has high weight."""
        components = {"interest_match": 0.9, "budget_fit": 0.5, "city_match": 0.5, "momentum": 0.5}
        product = {"category": "electronics"}
        deal = {"city": "Алматы"}
        interest_weights = {"electronics": 0.7}  # High weight from clicks
        
        chips = generate_explanation_chips(components, product, deal, interest_weights)
        
        assert "похоже на ваши клики" in chips
    
    def test_returns_2_to_4_chips(self):
        """Should return between 2 and 4 chips."""
        components = {"interest_match": 0.5, "budget_fit": 0.5, "city_match": 0.5, "momentum": 0.5}
        product = {"category": "electronics"}
        deal = {"city": "Алматы"}
        
        chips = generate_explanation_chips(components, product, deal, {})
        
        assert 2 <= len(chips) <= 4
    
    def test_chips_reflect_top_components(self):
        """Chips should reflect the top scoring components."""
        # High interest match, low everything else
        components = {"interest_match": 0.9, "budget_fit": 0.2, "city_match": 0.2, "momentum": 0.2}
        product = {"category": "electronics"}
        deal = {"city": "Алматы"}
        
        chips = generate_explanation_chips(components, product, deal, {"electronics": 0.6})
        
        # Should have interest-related chip
        assert any("электроника" in chip.lower() or "клики" in chip.lower() for chip in chips)
