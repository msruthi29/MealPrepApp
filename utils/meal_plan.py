"""
Meal plan generation and management.
"""
import pandas as pd
from typing import List, Optional
import itertools


def _recipe_name_from_foods(food_name: str, meal_name: str, selected_foods: List[str]) -> str:
    """Create a polished, cookbook-style recipe name using the selected ingredients."""
    clean_foods = [food for food in selected_foods if food and food != food_name]
    if not clean_foods:
        return f"{food_name} {meal_name} Plate"

    companion = clean_foods[0]
    if len(clean_foods) > 1:
        companion = f"{companion} & {clean_foods[1]}"

    meal_style = {
        "Breakfast": "Morning",
        "Lunch": "Light",
        "Dinner": "Cozy",
        "Snack": "Quick"
    }.get(meal_name, meal_name)

    return f"{meal_style} {food_name} with {companion}"


def _build_unique_day_sequence(selected_foods: List[str], meal_count: int) -> List[str]:
    """Return a unique food list for a single day without duplicates."""
    if not selected_foods:
        return []

    ordered = list(selected_foods)
    if len(ordered) >= meal_count:
        return ordered[:meal_count]

    repeated = ordered.copy()
    while len(repeated) < meal_count:
        repeated.extend(ordered)
    return repeated[:meal_count]


def _resolve_meal_types(meal_types: Optional[List[str]] = None, meals_per_day: int = 3) -> List[str]:
    """Return the selected meal labels in the order specified by the user."""
    if meal_types:
        cleaned = [str(item).strip() for item in meal_types if str(item).strip()]
        if cleaned:
            return cleaned

    default_meals = ["Breakfast", "Lunch", "Dinner", "Snack"]
    if meals_per_day <= len(default_meals):
        return default_meals[:meals_per_day]
    return default_meals + [f"Meal {idx}" for idx in range(len(default_meals) + 1, meals_per_day + 1)]


def generate_baby_plan(
    selected_foods: List[str],
    baby_df: pd.DataFrame,
    days: int = 1,
    meals_per_day: int = 3,
    excluded_foods: Optional[List[str]] = None,
    meal_types: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Generate a deterministic round-robin baby meal plan.
    
    Args:
        selected_foods: List of food items to include
        baby_df: Baby food dataframe
        days: Number of days (1-7)
        meals_per_day: Number of meals per day (1-5)
        excluded_foods: Foods to exclude
        meal_types: Optional list of meal names such as ["Breakfast", "Lunch", "Dinner"]
    
    Returns:
        DataFrame with columns: day, meal, food_item, texture_stage, safe_preparation, allergen
    """
    if not selected_foods:
        return pd.DataFrame(columns=["day", "meal", "recipe_name", "food_item", "texture_stage", "safe_preparation", "allergen"])
    
    excluded_foods = excluded_foods or []
    meal_labels = _resolve_meal_types(meal_types=meal_types, meals_per_day=meals_per_day)
    meals_per_day = len(meal_labels)
    
    # Filter to selected foods, excluding any in excluded list
    available_foods = [f for f in selected_foods if f not in excluded_foods]
    if not available_foods:
        return pd.DataFrame(columns=["day", "meal", "recipe_name", "food_item", "texture_stage", "safe_preparation", "allergen"])
    
    # Get food details from dataframe
    food_rows = baby_df[baby_df["food_item"].isin(available_foods)]
    
    plan_rows = []
    food_cycle = itertools.cycle(available_foods)
    
    for day in range(1, days + 1):
        day_foods = []
        for _ in range(len(meal_labels)):
            food_name = next(food_cycle)
            if food_name in day_foods:
                while food_name in day_foods:
                    food_name = next(food_cycle)
            day_foods.append(food_name)

        for meal_name, food_name in zip(meal_labels, day_foods):
            food_row = food_rows[food_rows["food_item"] == food_name].iloc[0]
            recipe_name = _recipe_name_from_foods(food_name, meal_name, available_foods)
            
            plan_rows.append({
                "day": day,
                "meal": meal_name,
                "recipe_name": recipe_name,
                "food_item": food_name,
                "texture_stage": food_row["texture_stage"],
                "safe_preparation": food_row["safe_preparation"],
                "allergen": food_row["allergen"]
            })
    
    return pd.DataFrame(plan_rows)


def generate_adult_plan(
    selected_foods: List[str],
    adult_df: pd.DataFrame,
    days: int = 1,
    meals_per_day: int = 3,
    excluded_foods: Optional[List[str]] = None,
    meal_types: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Generate a deterministic round-robin adult meal plan.
    
    Args:
        selected_foods: List of food items to include
        adult_df: Adult food dataframe
        days: Number of days (1-7)
        meals_per_day: Number of meals per day (1-5)
        excluded_foods: Foods to exclude
        meal_types: Optional list of meal names such as ["Breakfast", "Lunch", "Dinner"]
    
    Returns:
        DataFrame with columns: day, meal, food_item, measurable_quantity, allergen
    """
    if not selected_foods:
        return pd.DataFrame(columns=["day", "meal", "recipe_name", "food_item", "measurable_quantity", "allergen"])
    
    excluded_foods = excluded_foods or []
    meal_labels = _resolve_meal_types(meal_types=meal_types, meals_per_day=meals_per_day)
    meals_per_day = len(meal_labels)
    
    # Filter to selected foods, excluding any in excluded list
    available_foods = [f for f in selected_foods if f not in excluded_foods]
    if not available_foods:
        return pd.DataFrame(columns=["day", "meal", "recipe_name", "food_item", "measurable_quantity", "allergen"])
    
    # Get food details from dataframe
    food_rows = adult_df[adult_df["food_item"].isin(available_foods)]
    
    plan_rows = []
    food_cycle = itertools.cycle(available_foods)
    
    for day in range(1, days + 1):
        day_foods = []
        for _ in range(len(meal_labels)):
            food_name = next(food_cycle)
            if food_name in day_foods:
                while food_name in day_foods:
                    food_name = next(food_cycle)
            day_foods.append(food_name)

        for meal_name, food_name in zip(meal_labels, day_foods):
            food_row = food_rows[food_rows["food_item"] == food_name].iloc[0]
            recipe_name = _recipe_name_from_foods(food_name, meal_name, available_foods)
            
            plan_rows.append({
                "day": day,
                "meal": meal_name,
                "recipe_name": recipe_name,
                "food_item": food_name,
                "measurable_quantity": food_row["measurable_quantity"],
                "allergen": food_row["allergen"]
            })
    
    return pd.DataFrame(plan_rows)


def validate_plan_foods(plan: pd.DataFrame, available_foods: List[str]) -> bool:
    """
    Validate that all foods in a plan exist in the available foods list.
    
    Returns:
        True if all foods are valid
    """
    if plan.empty:
        return True
    
    plan_foods = plan["food_item"].unique().tolist()
    return all(f in available_foods for f in plan_foods)


def apply_plan_exclusions(
    plan: pd.DataFrame,
    excluded_foods: List[str]
) -> pd.DataFrame:
    """
    Remove rows with excluded foods from a plan.
    
    Returns:
        Updated plan DataFrame
    """
    if not excluded_foods or plan.empty:
        return plan
    
    return plan[~plan["food_item"].isin(excluded_foods)].reset_index(drop=True)
