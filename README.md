# MealNest

MealNest is a local-first Streamlit app for family meal planning using CSV-based food lists. It includes baby and adult meal planning, cookbook-style recipe names, daily meal scheduling, and AI feedback with a graceful fallback when no external AI key is configured.

## Overview

- 4 tabs: Food Items, Baby Nutrition & Meal Prep, Adult Nutrition & Meal Prep, and AI Feedback Chat
- CSV-driven datasets for baby and adult foods
- Meal plan generation for 1-7 days and 1-5 meals per day
- No repeated meals on the same day
- Cookbook-style recipe names for generated meals
- Local file persistence using CSV files and a feedback log
- No database and no authentication required

## Features

### Food Items
- View default baby and adult food lists
- Upload custom CSV files in the sidebar
- Validate CSV structure before use

### Baby Nutrition & Meal Prep
- Select foods with allergen filters
- Choose the number of days and meal types
- Generate daily meal plans without repeating items on the same day
- Show the food breakdown for each meal slot
- Display polished recipe-style titles

### Adult Nutrition & Meal Prep
- Search and filter adult foods
- Choose the number of days and meal types
- Build meal plans with balanced combinations
- Show per-day meal breakdowns and recipe names

### AI Feedback Chat
- Submit feedback in plain language
- Use Groq when configured
- Fall back to local deterministic feedback when AI is unavailable
- Log results to feedback.txt

## Tech Stack

- Streamlit
- Python
- Pandas
- NumPy
- uv
- Local CSV persistence

## Project Structure

```text
MealPrepApp/
├── app.py
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── README.md
├── feedback.txt
├── adult_food_items.csv
├── baby_food_items_under_12_months.csv
├── data/
│   ├── adult_food_items.csv
│   └── baby_food_items_under_12_months.csv
├── components/
│   ├── __init__.py
│   ├── food_items_tab.py
│   ├── baby_nutrition_tab.py
│   ├── adult_nutrition_tab.py
│   └── ai_feedback_chat_tab.py
├── utils/
│   ├── __init__.py
│   ├── csv_validation.py
│   ├── meal_plan.py
│   ├── session_data.py
│   ├── llm_agent.py
│   └── feedback_store.py
└── __pycache__/
```

## Setup

### 1. Install uv

Follow the installation guide for your platform:

- https://docs.astral.sh/uv/

### 2. Install dependencies

```bash
uv sync
```

### 3. Run the app

```bash
uv run streamlit run app.py
```

The app opens in the browser at http://localhost:8501 by default.

## CSV Data Format

### Adult CSV

```csv
food_item,allergen,measurable_quantity
Chicken breast,none,150 g
Salmon,fish,150 g
Eggs,egg,2 large eggs
```

### Baby CSV

```csv
food_id,food_item,texture_stage,safe_preparation,allergen
BABY-001,Iron-fortified infant cereal,smooth puree,"Prepare thin with breast milk, formula, or water; serve by spoon.",no
BABY-002,Sweet potato,smooth puree,"Steam until very soft, then mash or puree; no added salt.",no
```

## Validation Rules

The app validates:

- required columns
- empty values
- duplicate baby IDs
- malformed rows
- allergen normalization
- blank or missing food names

## Notes

- This project avoids a live USDA API dependency and works with local CSV data.
- The AI tab uses Groq only when configured; otherwise it falls back to local logic.
- Local CSV files and text logs are used for persistence; no external database is required.

## Disclaimer

This app is for meal planning and nutrition-data viewing only, not individualized medical or feeding advice. Consult healthcare professionals for individual dietary concerns or allergy guidance.

## Troubleshooting

### Streamlit fails to start

Check that dependencies are installed:

```bash
uv sync
```

Then run:

```bash
uv run streamlit run app.py
```

### CSV load errors

- Confirm the header names match the required fields
- Check for malformed commas or unquoted values in text fields
- Re-upload a valid CSV file

### AI chat not responding

This is expected if no Groq key is configured. The app will still provide fallback feedback without crashing.
