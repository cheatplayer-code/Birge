# Model Specification

## Overview

This is a **rule-based recommendation system**, NOT trained machine learning. All scores are calculated using explicit, transparent formulas with no black-box components.

## Scoring Formula

```
score = 0.40 * interest_match + 0.20 * budget_fit + 0.20 * city_match + 0.20 * momentum
```

All components are clamped between 0 and 1.

### Component Details

#### interest_match (weight: 0.40)
Measures alignment between user interests and product category/tags.

- Base score from category match: 0.5
- Additional score from matching tags: 0.1 each (max 0.5)
- Multiplied by adaptive weight from `users.interest_weights`
- Fallback: category/tag overlap when no user interests

#### budget_fit (weight: 0.20)
Measures how well product price matches user budget tier.

- Budget tiers: low (≤10000 KZT), mid (10000-50000 KZT), high (≥50000 KZT)
- Score peaks when price is within tier range
- Neutral (0.5) when no budget info available

#### city_match (weight: 0.20)
Binary match between user city and deal city.

- Same city: 1.0
- Different city: 0.0
- Missing info: 0.5

#### momentum (weight: 0.20)
Dynamically calculated from deal progress.

- Progress ratio: current_participants / target_participants (70% of score)
- Urgency boost: up to 0.2 near deadline
- Tier bonus: up to 0.1 for reaching discount tiers

**Momentum is NOT stored** - it is calculated on-the-fly from:
- `deals.current_participants`
- `deals.target_participants`
- `deals.deadline`
- `deals.tiers`
- `deals.created_at`

## Adaptive Interest Weights

User interest weights are stored in `public.users.interest_weights` as JSONB.

### Event Impacts

| Event Type | Weight Impact |
|------------|---------------|
| view       | +0.08         |
| click      | +0.30         |
| join       | +0.60         |
| share      | +0.20         |

### Weight Decay

All weights decay by 5% on each update to prevent old interests from dominating.

Constraints:
- Minimum weight: 0.1
- Maximum weight: 2.0

## Embeddings

Optional 12-dimensional vectors stored in `products.embedding`.

### Deterministic Fallback

When embeddings are missing, the system generates deterministic vectors from:
1. Category base vector (predefined per category)
2. Tag modifiers (small adjustments for tags like "new", "sale", "premium")

No external AI API is required.

## Trust Score

Rule-based calculation (0-100):

| Factor               | Max Points |
|---------------------|------------|
| SIM verified        | 30         |
| Completed deals     | 25         |
| Account age (90d)   | 20         |
| Total joins (20)    | 15         |
| Rapid join penalty  | -20        |

Verification threshold: 50 points

## Transparency Guarantees

1. **No trained models**: All calculations use explicit formulas
2. **Explainable scores**: Each recommendation includes `score_components` and `explanation_chips`
3. **Reproducible**: Same inputs always produce same outputs
4. **Auditable**: All logic is in plain Python code
