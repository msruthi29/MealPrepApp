"""
LLM agent for meal plan feedback and AI-guided refinement using Groq.
"""
import os
import json
import streamlit as st
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def parse_feedback_preferences(feedback_message: str, available_foods: List[str]) -> Dict[str, List[str]]:
    """Parse plain-language inclusion/exclusion requests from freeform user feedback."""
    message = (feedback_message or "").lower().strip()
    if not message:
        return {"include": [], "exclude": []}

    normalized_foods = []
    for food in available_foods:
        normalized_foods.append((food.lower(), food))

    included: List[str] = []
    excluded: List[str] = []

    patterns = {
        "include": ["include", "add", "keep", "prefer", "use", "add more of", "include more"],
        "exclude": ["exclude", "remove", "avoid", "skip", "do not include", "not include", "leave out", "drop", "without"],
    }

    for food_name, original in normalized_foods:
        if food_name not in message:
            continue

        if any(phrase in message for phrase in patterns["exclude"]):
            # If the sentence says 'exclude' and the food name is present, treat as exclusion.
            if any(phrase in message for phrase in ["exclude", "remove", "avoid", "skip", "leave out", "drop"]) and food_name in message:
                excluded.append(original)
                continue

        if any(phrase in message for phrase in patterns["include"]):
            if any(phrase in message for phrase in ["include", "add", "keep", "prefer", "use", "add more of"]) and food_name in message:
                included.append(original)
                continue

        # Generic fallback for any plain-language mention of a food item when the message is clearly negative
        if any(phrase in message for phrase in ["remove", "avoid", "skip", "drop", "don't include", "do not include", "without"]) and food_name in message:
            excluded.append(original)

    # Deduplicate while preserving order
    included = list(dict.fromkeys(included))
    excluded = list(dict.fromkeys(excluded))
    return {"include": included, "exclude": excluded}


class GroqAgent:
    """Agent for LLM-based meal plan feedback."""
    
    def __init__(self):
        """Initialize Groq agent."""
        self.api_key = GROQ_API_KEY
        self.model = GROQ_MODEL
        
        if not self.api_key:
            self.available = False
        else:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                self.available = True
            except Exception as e:
                st.warning(f"⚠️ Groq initialization failed: {e}")
                self.available = False
    
    def is_available(self) -> bool:
        """Check if Groq API is properly configured."""
        return self.available
    
    def process_feedback(
        self,
        plan_type: str,
        current_plan: List[Dict],
        available_foods: List[str],
        selected_foods: List[str],
        inclusions: List[str],
        exclusions: List[str],
        feedback_message: str
    ) -> Optional[Dict[str, Any]]:
        """
        Process user feedback and return meal plan recommendations.
        
        Args:
            plan_type: "Baby" or "Adult"
            current_plan: Current meal plan as list of dicts
            available_foods: All available foods
            selected_foods: Currently selected foods
            inclusions: Foods to explicitly include
            exclusions: Foods to explicitly exclude
            feedback_message: User's feedback text
        
        Returns:
            Dictionary with 'summary', 'approved_food_items', 'excluded_food_items', 
            'plan_considerations' or None if failed
        """
        if not self.available:
            st.warning("⚠️ Groq API not configured. Using deterministic plan updates only.")
            return None
        
        try:
            # Build the prompt
            prompt = self._build_prompt(
                plan_type,
                current_plan,
                available_foods,
                selected_foods,
                inclusions,
                exclusions,
                feedback_message
            )
            
            # Call Groq API
            response = self.client.messages.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Parse response
            response_text = response.content[0].text.strip()
            
            # Try to extract JSON from response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    st.warning("⚠️ Could not parse AI response. Using current plan.")
                    return None
            
            # Validate response structure
            if not isinstance(result, dict):
                st.warning("⚠️ Invalid AI response format.")
                return None
            
            # Ensure all required keys exist
            result = {
                "summary": result.get("summary", "Meal plan updated based on feedback."),
                "approved_food_items": result.get("approved_food_items", []),
                "excluded_food_items": result.get("excluded_food_items", []),
                "plan_considerations": result.get("plan_considerations", "")
            }
            
            # Validate food items against available foods
            result["approved_food_items"] = [
                f for f in result["approved_food_items"] if f in available_foods
            ]
            result["excluded_food_items"] = [
                f for f in result["excluded_food_items"] if f in available_foods
            ]
            
            return result
            
        except Exception as e:
            st.warning(f"⚠️ Groq API error: {str(e)}")
            return None
    
    def _build_prompt(
        self,
        plan_type: str,
        current_plan: List[Dict],
        available_foods: List[str],
        selected_foods: List[str],
        inclusions: List[str],
        exclusions: List[str],
        feedback_message: str
    ) -> str:
        """Build the prompt for the LLM."""
        plan_foods_str = ", ".join(selected_foods[:10])  # Limit output
        available_foods_str = ", ".join(available_foods[:20])  # Limit output
        
        prompt = f"""You are a helpful meal planning assistant for {plan_type.lower()} meal prep. 
        
Currently selected foods: {plan_foods_str}
All available foods: {available_foods_str}
Foods to include: {', '.join(inclusions) if inclusions else 'None specified'}
Foods to exclude: {', '.join(exclusions) if exclusions else 'None specified'}

User feedback: "{feedback_message}"

Please respond with ONLY valid JSON (no markdown, no extra text) containing exactly these keys:
- "summary": Brief summary of the recommended plan changes
- "approved_food_items": List of food items to include in the plan (must be from available foods)
- "excluded_food_items": List of food items to exclude from the plan (must be from available foods)
- "plan_considerations": Any special considerations or notes for the plan

Example response format:
{{"summary": "Added more vegetables...", "approved_food_items": ["Carrot", "Sweet potato"], "excluded_food_items": [], "plan_considerations": "Ensure variety..."}}

IMPORTANT RULES:
1. Return ONLY valid JSON with NO markdown formatting
2. Only include foods that are in the available foods list
3. Do NOT invent foods, nutrients, medical advice, or allergy information
4. Keep it concise and practical
5. This is meal planning support, NOT medical advice
"""
        return prompt


# Singleton instance
_groq_agent = None


def get_groq_agent() -> GroqAgent:
    """Get or create the Groq agent singleton."""
    global _groq_agent
    if _groq_agent is None:
        _groq_agent = GroqAgent()
    return _groq_agent


def is_groq_available() -> bool:
    """Check if Groq is properly configured."""
    agent = get_groq_agent()
    return agent.is_available()
