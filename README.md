# Toptama / Birge — ML/Data/API Layer

Transparent recommendation/ranking layer for the Birge hackathon group-buying marketplace.

## Architecture

- **Framework**: FastAPI (Python)
- **Database**: Supabase/PostgreSQL with pgvector
- **Testing**: pytest

**This is a rule-based recommendation system, NOT trained machine learning.** All scores are calculated using transparent, explicit formulas.

## Features

- **Transparent scoring formula**: `score = 0.40 * interest_match + 0.20 * budget_fit + 0.20 * city_match + 0.20 * momentum`
- **Adaptive interest weights**: Updated based on user events (view/click/join/share)
- **Deterministic embeddings**: 12-dimensional vectors generated from category/tags (no external API required)
- **Rule-based trust score**: Transparent calculation from SIM verification, completed deals, account age

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your Supabase credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
DEMO_MODE=true
```

### 3. Run Locally

```bash
python -m uvicorn src.main:app --reload
```

Server starts at `http://localhost:8000`

### 4. Run Tests

```bash
python -m pytest
```

### 5. Generate Demo Data

```bash
python scripts/seed.py
```

This creates `demo/demo_cases.json` with synthetic demo data.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/model-info` | GET | Model transparency information |
| `/recommendations?user_id=<uuid>` | GET | Get personalized ranked deals |
| `/events` | POST | Log user interaction events |
| `/trust-score?user_id=<uuid>` | GET | Get rule-based trust score |

### Example API Response

```bash
curl "http://localhost:8000/recommendations?user_id=user-001"
```

```json
{
  "success": true,
  "user_id": "user-001",
  "recommendations": [
    {
      "deal_id": "deal-001",
      "product_id": "prod-001",
      "score": 0.82,
      "components": {
        "interest_match": 0.9,
        "budget_fit": 0.8,
        "city_match": 1.0,
        "momentum": 0.6
      },
      "why": ["электроника", "Алматы", "в бюджете"],
      "product": {
        "name_ru": "Беспроводные наушники Sony",
        "name_kk": "Sony сымсыз құлаққаптары",
        "category": "electronics",
        "tags": ["smartphone", "audio"],
        "retail_price_kzt": 25200,
        "group_price_kzt": 17900,
        "image_url": "https://example.com/images/prod-001.jpg"
      },
      "deal": {
        "city": "Алматы",
        "current_participants": 14,
        "target_participants": 20,
        "deadline": "2024-12-20T23:59:59Z",
        "tiers": [{"min_participants": 10, "discount": 0.15}]
      }
    }
  ],
  "model_info": {
    "model_type": "transparent_hybrid_ranking",
    "version": "hackathon-v1",
    "not_trained_ml": true
  }
}
```

## Mounting in Main FastAPI App

Your teammate can mount this ML router into their FastAPI app:

```python
from fastapi import FastAPI
from src.api.routes import router as ml_router

app = FastAPI()

# Mount ML routes under /ml prefix
app.include_router(ml_router, prefix="/ml")
```

Then endpoints become:
- `/ml/health`
- `/ml/model-info`
- `/ml/recommendations?user_id=...`
- `/ml/events`
- `/ml/trust-score?user_id=...`

## Ranking Formula

```
score = 0.40 * interest_match
      + 0.20 * budget_fit
      + 0.20 * city_match
      + 0.20 * momentum
```

All components are clamped between 0 and 1.

## Event Impacts

| Event Type | Weight Impact |
|------------|---------------|
| view | +0.08 |
| click | +0.30 |
| join | +0.60 |
| share | +0.20 |

Two clicks on electronics will increase electronics recommendations.

## Demo Mode

When Supabase credentials are not configured or `DEMO_MODE=true`, the API uses synthetic demo data:
- 3 demo users
- 25 demo products
- 8 active deals (one at 14/20 participants)
- Sample events

## Database Schema

Run the migration in Supabase SQL Editor:
```sql
-- Copy contents of supabase/migrations/001_ml_schema.sql
```

Key tables:
- `users` - with `interest_weights` jsonb column for adaptive weights
- `products` - with localization fields (name_ru, name_kk) and optional 12-dim embedding
- `deals` - with dynamic momentum from participants/deadline/tiers (no stored momentum_score)
- `deal_members` - tracks deal participants with auto-updating trigger
- `events` - user interactions for adaptation

## Documentation

- [MODEL_SPEC.md](MODEL_SPEC.md) — Detailed model specification
- [API_CONTRACT.md](API_CONTRACT.md) — API request/response contracts

## Project Structure

```
src/
├── main.py               # FastAPI app entry point
├── config.py             # Settings management
├── api/
│   ├── routes.py         # API endpoint handlers
│   └── schemas.py        # Pydantic request/response models
├── model/
│   ├── types.py          # Data structures
│   ├── scoring.py        # Core ranking formula
│   ├── explain.py        # Explanation chips generation
│   ├── embeddings.py     # Deterministic vectors & demo data
│   ├── adaptation.py     # Interest weight updates
│   └── trust.py          # Trust score calculation
├── db/
│   └── supabase_client.py # Supabase client setup
└── utils/
    └── errors.py         # Custom exceptions

tests/
├── test_api.py           # API endpoint tests
└── model/
    ├── test_scoring.py   # Scoring formula tests
    ├── test_explain.py   # Explanation logic tests
    ├── test_adaptation.py # Adaptation logic tests
    └── test_trust.py     # Trust score tests

scripts/
└── seed.py               # Demo data generator

supabase/
└── migrations/
    └── 001_ml_schema.sql # Database schema
```

## License

Hackathon project — Toptama / Birge
