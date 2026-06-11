# API Contract

## ML/Recommendation API Endpoints

This document describes the ML/recommendation API layer only. Not a full marketplace API.

---

## GET /health

Health check endpoint.

### Response

```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "services": {
    "supabase": true,
    "ml_layer": true
  }
}
```

---

## GET /model-info

Returns model transparency information.

### Response

```json
{
  "model_type": "rule-based",
  "version": "0.1.0",
  "formula": "score = 0.40 * interest_match + 0.20 * budget_fit + 0.20 * city_match + 0.20 * momentum",
  "weights": {
    "interest_match": 0.40,
    "budget_fit": 0.20,
    "city_match": 0.20,
    "momentum": 0.20
  },
  "transparency_note": "This is a transparent rule-based ranking system, NOT trained machine learning."
}
```

---

## GET /recommendations?user_id=<uuid>

Returns personalized deal recommendations ranked by score.

### Parameters

| Parameter | Type   | Required | Description          |
|-----------|--------|----------|----------------------|
| user_id   | string | Yes      | User UUID            |
| limit     | number | No       | Max results (default: 20) |

### Response

```json
{
  "deals": [
    {
      "id": "deal-001",
      "product_id": "prod-001",
      "city": "Алматы",
      "current_participants": 14,
      "target_participants": 20,
      "tiers": [
        {"level": 1, "min_participants": 5, "discount_percent": 10},
        {"level": 2, "min_participants": 10, "discount_percent": 20},
        {"level": 3, "min_participants": 20, "discount_percent": 30}
      ],
      "deadline": "2024-01-18T10:30:00.000Z",
      "status": "active",
      "created_at": "2024-01-13T10:30:00.000Z",
      "product": {
        "id": "prod-001",
        "name_ru": "Беспроводные наушники",
        "category": "electronics",
        "tags": ["new", "popular"],
        "retail_price_kzt": 15000,
        "group_price_kzt": 12000
      },
      "score": 0.78,
      "score_components": {
        "interest_match": 0.9,
        "budget_fit": 0.7,
        "city_match": 1.0,
        "momentum": 0.6
      },
      "explanation_chips": ["electronics", "Алматы", "в бюджете", "быстро набирается"]
    }
  ],
  "user_id": "user-001",
  "generated_at": "2024-01-15T10:30:00.000Z",
  "model_info": "rule-based ranking v0.1.0"
}
```

### Score Components

All values clamped 0-1:

| Component      | Weight | Description                           |
|----------------|--------|---------------------------------------|
| interest_match | 0.40   | User interests vs product category    |
| budget_fit     | 0.20   | Product price vs user budget tier     |
| city_match     | 0.20   | User city vs deal city                |
| momentum       | 0.20   | Deal progress toward target           |

---

## POST /events

Log user interaction events and update adaptive weights.

### Request Body

```json
{
  "user_id": "user-001",
  "event_type": "click",
  "product_id": "prod-001",
  "deal_id": "deal-001",
  "category": "electronics",
  "metadata": {}
}
```

### Event Types

| Type   | Impact | Description                    |
|--------|--------|--------------------------------|
| view   | +0.08  | User viewed product/deal       |
| click  | +0.30  | User clicked product/deal      |
| join   | +0.60  | User joined deal               |
| share  | +0.20  | User shared deal               |

### Response

```json
{
  "success": true,
  "event": {
    "id": "event-001",
    "user_id": "user-001",
    "event_type": "click",
    "product_id": "prod-001",
    "deal_id": "deal-001",
    "category": "electronics",
    "created_at": "2024-01-15T10:30:00.000Z"
  },
  "message": "Event logged successfully"
}
```

### Side Effects

- Event is stored in `events` table
- User's `interest_weights` are updated if category is provided
- Two clicks on same category significantly increase that category's weight

---

## GET /trust-score?user_id=<uuid>

Returns rule-based trust score for a user.

### Parameters

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| user_id   | string | Yes      | User UUID   |

### Response

```json
{
  "user_id": "user-001",
  "trust_score": 65,
  "factors": {
    "sim_verified": true,
    "completed_deals": 3,
    "total_joins": 8,
    "account_age_days": 30,
    "rapid_join_penalty": 0
  },
  "is_verified": true
}
```

### Trust Score Calculation

| Factor              | Max Points |
|---------------------|------------|
| SIM verified        | 30         |
| Completed deals     | 25         |
| Account age (90d)   | 20         |
| Total joins (20)    | 15         |
| Rapid join penalty  | -20        |

Score is clamped 0-100. Verification threshold: 50.

---

## Error Responses

### 400 Bad Request

```json
{
  "error": "user_id parameter is required"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error"
}
```

---

## Mounting in Teammate's FastAPI App

To mount this ML router under `/ml` prefix in your FastAPI app:

```python
from src.api.routes import router as ml_router

app.include_router(ml_router, prefix="/ml")
```

This will make all endpoints available under `/ml`:
- `GET /ml/health`
- `GET /ml/model-info`
- `GET /ml/recommendations?user_id=<uuid>`
- `POST /ml/events`
- `GET /ml/trust-score?user_id=<uuid>`
