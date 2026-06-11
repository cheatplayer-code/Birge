## Project Context

This repository is for the hackathon project Toptama / Birge.

The full product is a mobile-first group-buying marketplace.

Your current responsibility is ONLY the ML/data/API layer implemented in Python with FastAPI.

Do NOT build the full marketplace UI.
Do NOT implement onboarding screens.
Do NOT implement product detail UI.
Do NOT implement payment flow.
Do NOT implement SIM verification UI.
Do NOT implement profile UI.
Do NOT implement live presentation UI.
Do NOT redesign the app.

## Current ML Goal

Implement a transparent, explainable recommendation system for the marketplace feed.

The ranking formula must be:

score = 0.40 * interest_match
+ 0.20 * budget_fit
+ 0.20 * city_match
+ 0.20 * momentum

The ML layer should return ranked deals with score components and explanation chips.

Example explanation chips:

* “электроника”
* “Алматы”
* “в бюджете”
* “быстро набирается”
* “похоже на ваши клики”

## Main ML Features

### 1. Personal ranking feed

Rank active deals for a user using:

* user interests
* product category/tags
* optional product embeddings
* user budget tier
* user city
* deal momentum

If embeddings are missing, use tag/category overlap as fallback.

### 2. Explainability

Every recommendation must include:

* total score
* score components
* short explanation chips
* no fake AI claims

The frontend should be able to show:
“Почему рекомендовано: электроника · Алматы · в бюджете”

### 3. Event logging and adaptation

Log events:

* view
* click
* join
* share

Events should update user interest weights.

Example:
Two clicks on electronics should increase electronics ranking.

### 4. Optional trust score

Trust score is rule-based only:

* SIM verified gives positive score
* completed deals increase score
* abnormal rapid joins decrease score

Do not claim this is a trained ML model.

## Database Scope

Use Supabase/Postgres.

Required tables:

* users
* products
* deals
* deal_members
* events

Products may include pgvector embeddings, but the demo must work without external embedding APIs.

The live demo must not depend on paid or unstable AI API calls.

## API Scope

Required endpoints:

GET /recommendations?user_id=<uuid>

Returns ranked recommendations:

* deal_id
* product_id
* score
* components
* why
* product summary
* deal summary

POST /events

Accepts:

* user_id
* event_type
* product_id
* deal_id
* category
* metadata

Inserts event and updates user interest weights.

Optional:
GET /model-info
GET /trust-score?user_id=<uuid>

## Code Rules

* Use Python with FastAPI.
* Keep ML logic separate from API route logic.
* Put pure ML functions in src/model/.
* Keep Supabase access in src/db/.
* Do not hardcode secrets.
* Use .env.example for required environment variables.
* Do not invent fake production metrics.
* Synthetic seed data is allowed, but label it clearly as demo data.
* Do not add unnecessary dependencies.
* Prefer simple, readable code over clever abstractions.
* Add tests for scoring, explanations, adaptation, and edge cases.

## Required File Structure

Aim for this structure:

src/__init__.py
src/main.py
src/config.py

src/api/__init__.py
src/api/routes.py
src/api/schemas.py

src/model/__init__.py
src/model/types.py
src/model/scoring.py
src/model/explain.py
src/model/embeddings.py
src/model/adaptation.py
src/model/trust.py

src/db/__init__.py
src/db/supabase_client.py

src/utils/__init__.py
src/utils/errors.py

supabase/migrations/001_ml_schema.sql

scripts/seed.py

tests/test_api.py
tests/model/test_scoring.py
tests/model/test_explain.py
tests/model/test_adaptation.py
tests/model/test_trust.py

## Done Means

A task is done only when:

* The code builds or clear run instructions are provided.
* The recommendation endpoint returns valid JSON.
* The ranking formula is implemented exactly.
* Score components are clamped between 0 and 1.
* Explanations are derived from score components.
* Bad input is handled safely.
* Demo seed data exists.
* There is a fallback if embeddings are missing.
* Tests or manual verification commands are provided.
* Changed files are listed.
* Remaining risks are stated honestly.

## After Every Task

After coding, report:

1. Files changed
2. What changed
3. How to run
4. How to test
5. Example API response
6. Remaining risks
7. Whether any API contract changed

## Forbidden

Do not:

* build frontend UI
* rewrite the whole project
* change unrelated files
* introduce a separate Python ML service
* add a huge training pipeline
* claim collaborative filtering
* claim demand prediction
* claim neural network training
* fake accuracy
* fake real users
* fake sponsor/API integration
* expose API keys
* remove fallback logic
