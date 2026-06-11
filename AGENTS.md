AGENTS.md

This repository uses `QWEN.md` as the main agent instruction file.

Before making any changes, read `QWEN.md` and follow it strictly.

Summary:

* Work only on the ML/data/API layer implemented in Python with FastAPI.
* Do not build frontend UI.
* Do not implement onboarding, payment, SIM UI, profile UI, or presentation UI.
* Keep the recommendation formula exact:
  score = 0.40 * interest_match
  + 0.20 * budget_fit
  + 0.20 * city_match
  + 0.20 * momentum
* Keep ML logic separate from API route logic (src/model/ for ML, src/api/ for routes).
* Return stable structured JSON for frontend.
* Add tests for scoring, explanation, adaptation, and edge cases using pytest.
* Do not fake metrics, users, AI claims, or production data.
* After every task, list changed files, how to run, how to test, and remaining risks.

If any instruction conflicts with `QWEN.md`, follow `QWEN.md`.
