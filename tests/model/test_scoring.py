"""Tests for ML model scoring functions."""

import pytest
from src.model.scoring import (
    clamp,
    calculate_interest_match,
    calculate_budget_fit,
    calculate_city_match,
    calculate_momentum,
    calculate_final_score,
    rank_deals_for_user,
)


class TestClamp:
    """Test clamp function."""
    
    def test_clamp_within_range(self):
        assert clamp(0.5) == 0.5
        assert clamp(0.0) == 0.0
        assert clamp(1.0) == 1.0
    
    def test_clamp_above_range(self):
        assert clamp(1.5) == 1.0
        assert clamp(2.0) == 1.0
    
    def test_clamp_below_range(self):
        assert clamp(-0.5) == 0.0
        assert clamp(-1.0) == 0.0


class TestCalculateInterestMatch:
    """Test interest match calculation."""
    
    def test_category_match_with_weight(self):
        user = {
            "interests": ["electronics"],
            "interest_weights": {"electronics": 0.8}
        }
        product = {"category": "electronics", "tags": []}
        
        score = calculate_interest_match(user, product)
        assert 0.6 <= score <= 1.0  # Should be high due to category match + weight
    
    def test_no_match_returns_low_score(self):
        user = {
            "interests": ["fashion"],
            "interest_weights": {}
        }
        product = {"category": "electronics", "tags": []}
        
        score = calculate_interest_match(user, product)
        assert 0.0 <= score <= 0.3  # Should be low
    
    def test_tag_overlap(self):
        user = {
            "interests": ["smartphone"],
            "interest_weights": {"smartphone": 0.6}
        }
        product = {"category": "toys", "tags": ["smartphone"]}
        
        score = calculate_interest_match(user, product)
        assert score > 0.0  # Should have some score from tag overlap


class TestCalculateBudgetFit:
    """Test budget fit calculation."""
    
    def test_low_budget_perfect_fit(self):
        assert calculate_budget_fit("low", 8000) == 1.0
    
    def test_low_budget_decay(self):
        score = calculate_budget_fit("low", 15000)
        assert 0.5 <= score < 1.0
    
    def test_mid_budget_perfect_fit(self):
        assert calculate_budget_fit("mid", 30000) == 1.0
    
    def test_mid_budget_cheap_item(self):
        score = calculate_budget_fit("mid", 5000)
        assert 0.7 <= score < 1.0  # Slight penalty for very cheap
    
    def test_high_budget_expensive_item(self):
        assert calculate_budget_fit("high", 80000) == 1.0
    
    def test_all_scores_clamped(self):
        """Verify all budget fit scores are clamped 0-1."""
        for tier in ["low", "mid", "high"]:
            for price in [1000, 10000, 50000, 100000, 500000]:
                score = calculate_budget_fit(tier, price)
                assert 0.0 <= score <= 1.0


class TestCalculateCityMatch:
    """Test city match calculation."""
    
    def test_same_city_returns_one(self):
        assert calculate_city_match("Алматы", "Алматы") == 1.0
    
    def test_same_city_case_insensitive(self):
        assert calculate_city_match("алматы", "АЛМАТЫ") == 1.0
    
    def test_different_kazakhstan_cities(self):
        score = calculate_city_match("Алматы", "Астана")
        assert score == 0.35
    
    def test_missing_city_returns_zero(self):
        assert calculate_city_match("", "Алматы") == 0.0
        assert calculate_city_match("Алматы", "") == 0.0
    
    def test_same_city_ranks_higher(self):
        """Same city should rank higher than different city when other factors equal."""
        same_city = calculate_city_match("Алматы", "Алматы")
        diff_city = calculate_city_match("Алматы", "Астана")
        assert same_city > diff_city


class TestCalculateMomentum:
    """Test momentum calculation."""
    
    def test_high_progress_high_momentum(self):
        deal = {
            "current_participants": 18,
            "target_participants": 20,
            "deadline": "2025-12-31T23:59:59Z",
            "created_at": "2024-01-01T00:00:00Z"
        }
        score = calculate_momentum(deal)
        assert score > 0.5  # High progress should give good momentum
    
    def test_low_progress_low_momentum(self):
        deal = {
            "current_participants": 1,
            "target_participants": 20,
            "deadline": "2025-12-31T23:59:59Z",
            "created_at": "2024-01-01T00:00:00Z"
        }
        score = calculate_momentum(deal)
        assert score < 0.3  # Low progress should give low momentum
    
    def test_all_scores_clamped(self):
        """Verify all momentum scores are clamped 0-1."""
        deals = [
            {"current_participants": 0, "target_participants": 10},
            {"current_participants": 5, "target_participants": 10},
            {"current_participants": 10, "target_participants": 10},
            {"current_participants": 20, "target_participants": 10},  # Over target
        ]
        for deal in deals:
            score = calculate_momentum(deal)
            assert 0.0 <= score <= 1.0


class TestCalculateFinalScore:
    """Test final score calculation with exact formula."""
    
    def test_exact_formula_weights(self):
        """Verify exact formula: 0.40*interest + 0.20*budget + 0.20*city + 0.20*momentum"""
        components = {
            "interest_match": 1.0,
            "budget_fit": 0.5,
            "city_match": 0.5,
            "momentum": 0.5
        }
        expected = 0.40 * 1.0 + 0.20 * 0.5 + 0.20 * 0.5 + 0.20 * 0.5
        expected = 0.40 + 0.10 + 0.10 + 0.10  # = 0.70
        
        score = calculate_final_score(components)
        assert abs(score - expected) < 0.001
    
    def test_all_components_clamped(self):
        """Verify final score is clamped 0-1."""
        # Even with extreme inputs, should be clamped
        components = {
            "interest_match": 1.0,
            "budget_fit": 1.0,
            "city_match": 1.0,
            "momentum": 1.0
        }
        score = calculate_final_score(components)
        assert score == 1.0
        
        components = {
            "interest_match": 0.0,
            "budget_fit": 0.0,
            "city_match": 0.0,
            "momentum": 0.0
        }
        score = calculate_final_score(components)
        assert score == 0.0


class TestRankDealsForUser:
    """Test deal ranking."""
    
    def test_same_city_ranks_higher(self):
        """Same city should rank higher when other factors equal."""
        user = {
            "id": "00000000-0000-0000-0000-000000000001",
            "budget_tier": "mid",
            "city": "Алматы",
            "interests": ["electronics"],
            "interest_weights": {"electronics": 0.5}
        }
        
        products = {
            "10000000-0000-0000-0000-000000000001": {
                "id": "10000000-0000-0000-0000-000000000001",
                "name_ru": "Product 1",
                "name_kk": "Product 1 KK",
                "category": "electronics",
                "tags": [],
                "retail_price_kzt": 20000,
                "group_price_kzt": 15000
            },
            "prod-002": {
                "id": "prod-002",
                "name_ru": "Product 2",
                "name_kk": "Product 2 KK",
                "category": "electronics",
                "tags": [],
                "retail_price_kzt": 20000,
                "group_price_kzt": 15000
            }
        }
        
        deals = [
            {
                "id": "20000000-0000-0000-0000-000000000001",
                "product_id": "10000000-0000-0000-0000-000000000001",
                "city": "Алматы",  # Same city
                "current_participants": 10,
                "target_participants": 20
            },
            {
                "id": "deal-002",
                "product_id": "prod-002",
                "city": "Астана",  # Different city
                "current_participants": 10,
                "target_participants": 20
            }
        ]
        
        recommendations = rank_deals_for_user(user, deals, products)
        
        # Same city deal should rank higher
        assert recommendations[0]["deal"]["city"] == "Алматы"
    
    def test_in_budget_ranks_higher(self):
        """In-budget deal should rank higher when other factors equal."""
        user = {
            "id": "00000000-0000-0000-0000-000000000001",
            "budget_tier": "low",
            "city": "Алматы",
            "interests": ["electronics"],
            "interest_weights": {"electronics": 0.5}
        }
        
        products = {
            "10000000-0000-0000-0000-000000000001": {
                "id": "10000000-0000-0000-0000-000000000001",
                "name_ru": "Cheap Product",
                "name_kk": "Cheap Product KK",
                "category": "electronics",
                "tags": [],
                "retail_price_kzt": 10000,
                "group_price_kzt": 8000  # In budget
            },
            "prod-002": {
                "id": "prod-002",
                "name_ru": "Expensive Product",
                "name_kk": "Expensive Product KK",
                "category": "electronics",
                "tags": [],
                "retail_price_kzt": 100000,
                "group_price_kzt": 80000  # Out of budget
            }
        }
        
        deals = [
            {
                "id": "20000000-0000-0000-0000-000000000001",
                "product_id": "10000000-0000-0000-0000-000000000001",
                "city": "Алматы",
                "current_participants": 10,
                "target_participants": 20
            },
            {
                "id": "deal-002",
                "product_id": "prod-002",
                "city": "Алматы",
                "current_participants": 10,
                "target_participants": 20
            }
        ]
        
        recommendations = rank_deals_for_user(user, deals, products)
        
        # In-budget deal should rank higher
        assert recommendations[0]["product"]["group_price_kzt"] == 8000
