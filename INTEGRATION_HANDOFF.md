# ML API Integration Handoff

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- fastapi
- uvicorn
- pydantic
- numpy
- python-dateutil
- supabase (optional, for production DB)
- pytest (for testing)

### Run the ML API Standalone

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Mount Router in Your App

```python
from fastapi import FastAPI
from src.api.routes import router as ml_router

app = FastAPI()

# Mount the ML router with /ml prefix
app.include_router(ml_router, prefix="/ml")
```

## Final Endpoint List

All endpoints are prefixed with `/ml` when mounted:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ml/health` | Health check |
| GET | `/ml/model-info` | Model information |
| GET | `/ml/recommendations?user_id=<uuid>` | Get personalized recommendations |
| POST | `/ml/events` | Log user event |
| GET | `/ml/trust-score?user_id=<uuid>` | Get user trust score |

## Example Requests/Responses

### Health Check

```bash
curl http://localhost:8000/ml/health
```

Response:
```json
{
  "status": "healthy",
  "version": "hackathon-v1",
  "demo_mode": true,
  "supabase_connected": true
}
```

### Model Info

```bash
curl http://localhost:8000/ml/model-info
```

Response:
```json
{
  "model_type": "transparent_hybrid_ranking",
  "version": "hackathon-v1",
  "formula": "0.40 * interest_match + 0.20 * budget_fit + 0.20 * city_match + 0.20 * momentum",
  "not_trained_ml": true,
  "features": ["interest_match", "budget_fit", "city_match", "momentum"]
}
```

### Recommendations

```bash
curl "http://localhost:8000/ml/recommendations?user_id=00000000-0000-0000-0000-000000000001"
```

Response:
```json
{
  "success": true,
  "user_id": "00000000-0000-0000-0000-000000000001",
  "recommendations": [
    {
      "deal_id": "20000000-0000-0000-0000-000000000001",
      "product_id": "10000000-0000-0000-0000-000000000001",
      "score": 0.874,
      "components": {
        "interest_match": 0.8,
        "budget_fit": 1.0,
        "city_match": 1.0,
        "momentum": 0.77
      },
      "why": ["похоже на ваши клики", "Алматы", "в бюджете", "быстро набирается"],
      "product": {...},
      "deal": {...}
    }
  ]
}
```

### Log Event

```bash
curl -X POST http://localhost:8000/ml/events \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "00000000-0000-0000-0000-000000000001",
    "event_type": "click",
    "category": "electronics",
    "metadata": {}
  }'
```

Response:
```json
{
  "success": true,
  "message": "Event click logged (demo mode)",
  "weight_update": {
    "category": "electronics",
    "impact": 0.3
  }
}
```

### Trust Score

```bash
curl "http://localhost:8000/ml/trust-score?user_id=00000000-0000-0000-0000-000000000001"
```

Response:
```json
{
  "success": true,
  "user_id": "00000000-0000-0000-0000-000000000001",
  "trust_score": 60,
  "factors": {
    "sim_verified": false,
    "completed_deals": 0,
    "completed_deals_bonus": 0,
    "account_age_bonus": false,
    "event_diversity": true,
    "rapid_join_penalty": false,
    "base_score": 50,
    "final_score": 60
  }
}
```

## What is Demo-Only

The following features run in demo mode without a database:

1. **Demo Data**: Pre-seeded users, products, deals in `demo/demo_cases.json`
2. **In-Memory Events**: Events are stored temporarily and reset on restart
3. **Trust Scores**: Computed from demo events only
4. **Recommendations**: Based on demo data with transparent scoring

Demo mode is active when Supabase credentials are not configured.

## What Requires Supabase Credentials

For production use, set these environment variables:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
```

With Supabase connected:
- User profiles persist across sessions
- Events are stored in `user_events` table
- Deals are loaded from `deals` table
- Products are loaded from `products` table
- Trust scores include verified SIM and completed deal bonuses

## Important Note: Not Trained ML

**This is NOT a trained machine learning model.**

The ranking system uses **transparent hybrid rule-based scoring**:

```
score = 0.40 * interest_match + 0.20 * budget_fit + 0.20 * city_match + 0.20 * momentum
```

Features:
- `interest_match`: Cosine similarity between user interests and product embeddings
- `budget_fit`: How well price matches user's budget tier
- `city_match`: Whether deal is in user's city
- `momentum`: Deal progress ratio (current/target participants)

This approach was chosen for:
- Transparency (users see why items are recommended)
- No training data required
- Easy to explain to stakeholders
- Works immediately with cold-start users

## Testing

Run tests:
```bash
python -m pytest -v
```

## Files Changed

- `demo/demo_cases.json` - Updated IDs to valid UUID format
- `tests/test_api.py` - Updated test IDs to UUIDs
- `tests/model/test_scoring.py` - Updated test IDs to UUIDs
- `.gitignore` - Fixed formatting (removed markdown code blocks)

## Demo IDs

All demo data now uses valid UUID strings:
- Users: `00000000-0000-0000-0000-000000000001`, etc.
- Products: `10000000-0000-0000-0000-000000000001`, etc.
- Deals: `20000000-0000-0000-0000-000000000001`, etc.

These are compatible with Supabase UUID primary keys.
