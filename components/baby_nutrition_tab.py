"""
Tab 2: Baby Nutrition & Meal Prep
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List
from utils.meal_plan import generate_baby_plan, validate_plan_foods


def render_baby_nutrition_tab(baby_df: pd.DataFrame):
    """
    Render the Baby Nutrition & Meal Prep tab.
    """
    st.header("👶 Baby Nutrition & Meal Prep")
    
    if baby_df.empty:
        st.warning("No baby food data available. Please upload a valid CSV.")
        return
    
    # Safety notice
    st.warning(
        "⚠️ **Safety Disclaimer**: This app is for organization and nutrition-data viewing only, "
        "not individualized medical or feeding advice. Caregivers must use foods and textures "
        "appropriate for developmental readiness, supervise eating, and consult a pediatric "
        "clinician for individual feeding or allergy questions."
    )
    
    # Food selection
    st.subheader("Select Baby Foods")
    
    all_foods = baby_df["food_item"].tolist()
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_foods = st.multiselect(
            "Choose foods to analyze",
            all_foods,
            key="selected_baby_foods_input"
        )
    
    with col2:
        # Allergen filter
        all_allergens = baby_df["allergen"].unique().tolist()
        allergens_to_exclude = st.multiselect(
            "Exclude foods with allergens",
            sorted([a for a in all_allergens if a != "no"]),
            key="baby_allergen_filter"
        )
    
    # Apply allergen filter
    if allergens_to_exclude:
        filtered_foods = baby_df[~baby_df["allergen"].isin(allergens_to_exclude)]["food_item"].tolist()
        selected_foods = [f for f in selected_foods if f in filtered_foods]
    
    if not selected_foods:
        st.info("Select foods above to see meal prep options.")
        return
    
    matched_foods = selected_foods
    
    st.info("📋 Food information from your dataset. For detailed nutrition data, upload a CSV with nutritional columns or use an external nutrition database.")
    
    # Display food details
    st.subheader("Selected Foods Information")
    
    # Display food details from CSV
    foods_df = baby_df[baby_df["food_item"].isin(matched_foods)][['food_item', 'texture_stage', 'safe_preparation', 'allergen']]
    st.dataframe(foods_df, use_container_width=True, hide_index=True)
    
    st.caption("Food information from your uploaded dataset.")
    
    # Meal prep checklist
    st.subheader("Baby Meal Prep Checklist")
    
    days = st.slider("Number of days", 1, 7, 1, key="baby_days")
    meal_types = st.multiselect(
        "Meal types",
        ["Breakfast", "Lunch", "Dinner", "Snack"],
        default=["Breakfast", "Lunch", "Dinner"],
        key="baby_meal_types"
    )

    if not meal_types:
        st.info("Please choose at least one meal type to build the plan.")
        return
    
    if st.button("Generate Checklist", key="gen_baby_checklist"):
        plan = generate_baby_plan(matched_foods, baby_df, days, len(meal_types), meal_types=meal_types)
        st.session_state.baby_plan = plan
    
    if not st.session_state.baby_plan.empty:
        st.subheader("Generated Checklist")
        st.dataframe(st.session_state.baby_plan[["day", "meal", "recipe_name", "food_item", "texture_stage", "safe_preparation", "allergen"]], use_container_width=True, hide_index=True)

        st.subheader("Daily Breakdown")
        for day in sorted(st.session_state.baby_plan["day"].unique().tolist()):
            day_rows = st.session_state.baby_plan[st.session_state.baby_plan["day"] == day]
            st.write(f"**Day {day}**")
            for meal in meal_types:
                meal_row = day_rows[day_rows["meal"] == meal]
                if not meal_row.empty:
                    recipe_name = meal_row.iloc[0]["recipe_name"]
                    food_items = meal_row.iloc[0]["food_item"]
                    st.write(f"- {meal}: {recipe_name} ({food_items})")
                else:
                    st.write(f"- {meal}: No item selected")
        
        # Editable plan
        edited_plan = st.data_editor(
            st.session_state.baby_plan,
            use_container_width=True,
            key="baby_plan_editor"
        )
        
        # Download plan
        csv_data = edited_plan.to_csv(index=False)
        st.download_button(
            label="📥 Download Checklist as CSV",
            data=csv_data,
            file_name="baby_meal_prep_checklist.csv",
            mime="text/csv",
            key="download_baby_plan"
        )
