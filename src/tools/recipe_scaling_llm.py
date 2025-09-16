#!/usr/bin/env python3.11
"""
LLM-First Recipe Scaling & Unit Conversion Tool

This tool uses the LLM's natural language understanding to scale recipes,
detect serving sizes from prompts, and handle unit conversions intelligently.
"""

from smolagents import Tool
import json
import time
from openai import OpenAI

# Telemetry imports (optional)
try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False


class RecipeScalingLLMTool(Tool):
    """
    LLM-powered recipe scaling tool that uses natural language understanding
    to scale recipes, detect serving sizes, and handle unit conversions.
    
    Telemetry Tracking:
    - scaling.original_servings: Original recipe servings
    - scaling.target_servings: Target servings requested
    - scaling.scaling_factor: Mathematical scaling factor (e.g., 2.0 for 4→8)
    - scaling.scaling_method: Method used (proportional, time_adjusted)
    - scaling.unit_conversions_count: Number of unit conversions performed
    - scaling.success_rate: Scaling success percentage
    """
    
    name: str = "recipe_scaling_llm"
    description: str = (
        "Scales recipes to target serving sizes using LLM natural language understanding. "
        "Detects serving sizes from user prompts, scales ingredients and instructions, "
        "and handles unit conversions intelligently. Much more flexible than deterministic approaches."
    )
    output_type: str = "string"
    
    def __init__(self):
        super().__init__()
        # Initialize OpenAI client for LLM calls
        self.client = OpenAI(
            base_url="http://192.168.1.27:1234/v1",
            api_key="dummy"  # Not needed for local server
        )
    
    inputs: dict = {
        "recipe_data": {
            "type": "string", 
            "description": "JSON string containing the recipe data with ingredients and instructions"
        },
        "target_servings": {
            "type": "string", 
            "description": "Target number of servings (e.g., '4', '6', '8') or 'auto' to detect from prompt"
        },
        "user_prompt": {
            "type": "string", 
            "description": "Original user prompt to detect serving size if target_servings is 'auto'",
            "nullable": True
        }
    }
    
    def forward(self, recipe_data: str, target_servings: str, user_prompt: str = None) -> str:
        """
        Scale recipe to target serving size using LLM.
        
        Args:
            recipe_data (str): JSON string containing recipe data
            target_servings (str): Target number of servings or 'auto'
            user_prompt (str): Original user prompt for serving size detection
            
        Returns:
            str: JSON string with scaled recipe data
        """
        # Start telemetry span if available
        if TELEMETRY_AVAILABLE:
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span("recipe_scaling_llm") as span:
                span.set_attribute("tool.name", "recipe_scaling_llm")
                span.set_attribute("tool.target_servings", target_servings)
                span.set_attribute("tool.user_prompt", user_prompt or "")
                return self._scale_recipe_with_telemetry(recipe_data, target_servings, user_prompt, span)
        else:
            return self._scale_recipe_with_telemetry(recipe_data, target_servings, user_prompt, None)
    
    def _scale_recipe_with_telemetry(self, recipe_data: str, target_servings: str, user_prompt: str = None, span=None) -> str:
        """
        Internal method to scale recipe with telemetry tracking.
        """
        try:
            # Parse recipe data
            recipe = json.loads(recipe_data)
            
            if not recipe.get('success') or not recipe.get('recipe'):
                return json.dumps({
                    "success": False,
                    "error": "Invalid recipe data provided",
                    "original_recipe": recipe
                })
            
            recipe_info = recipe['recipe']
            
            # Use LLM to determine target servings and scale the recipe
            scaled_result = self._scale_with_llm(recipe_info, target_servings, user_prompt, span)
            
            # Add telemetry attributes for successful scaling
            if span and scaled_result.get('success'):
                scaling_info = scaled_result.get('scaling_info', {})
                span.set_attribute("scaling.original_servings", scaling_info.get('original_servings', 'unknown'))
                span.set_attribute("scaling.target_servings", scaling_info.get('target_servings', 'unknown'))
                span.set_attribute("scaling.scaling_factor", scaling_info.get('scaling_factor', 'unknown'))
                span.set_attribute("scaling.scaling_method", scaling_info.get('scaling_method', 'unknown'))
                span.set_attribute("scaling.unit_conversions_count", len(scaling_info.get('unit_conversions', [])))
                span.set_status(Status(StatusCode.OK))
            elif span:
                span.set_status(Status(StatusCode.ERROR, "Scaling failed"))
            
            return json.dumps(scaled_result)
            
        except json.JSONDecodeError as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to parse recipe data: {str(e)}",
                "original_recipe": recipe_data
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Scaling failed: {str(e)}",
                "original_recipe": recipe_data
            })
    
    def _scale_with_llm(self, recipe: dict, target_servings: str, user_prompt: str = None, span=None) -> dict:
        """
        Use LLM to scale recipe with natural language understanding.
        
        Args:
            recipe (dict): Recipe data
            target_servings (str): Target servings or 'auto'
            user_prompt (str): User prompt for serving size detection
            
        Returns:
            dict: Scaled recipe data
        """
        # Prepare the recipe data for the LLM
        recipe_text = self._format_recipe_for_llm(recipe)
        
        prompt = f"""You are a recipe scaling expert. Scale this recipe to the target serving size.

ORIGINAL RECIPE:
{recipe_text}

TARGET SERVINGS: {target_servings}
USER PROMPT: {user_prompt or 'Not provided'}

INSTRUCTIONS:
1. If target_servings is 'auto', analyze the user_prompt to determine the appropriate serving size
2. Scale all ingredient amounts proportionally
3. Update instruction text with new amounts where appropriate
4. Convert units to more appropriate sizes when needed (e.g., 16 cups → 1 gallon)
5. Format amounts in the most readable way (fractions for small amounts, decimals for larger)
6. Update cooking times appropriately (cooking time doesn't scale linearly)

Return a JSON object with this exact structure:
{{
    "success": true,
    "original_recipe": {json.dumps(recipe)},
    "scaled_recipe": {{
        "title": "Scaled recipe title",
        "description": "Updated description if needed",
        "url": "original URL",
        "ingredients": [
            {{"ingredient": "2 cups flour", "amount": "2", "unit": "cups"}},
            {{"ingredient": "1 large egg", "amount": "1", "unit": "large"}}
        ],
        "instructions": [
            {{"step": 1, "instruction": "Updated instruction with scaled amounts"}},
            {{"step": 2, "instruction": "Second instruction with scaled amounts"}}
        ],
        "prep_time": "Updated prep time",
        "cook_time": "Updated cook time", 
        "total_time": "Updated total time",
        "servings": "Target serving count",
        "dietary_tags": ["original tags"],
        "difficulty": "original difficulty",
        "source": "original source"
    }},
    "scaling_info": {{
        "original_servings": "Original serving count",
        "target_servings": "Target serving count",
        "scaling_factor": "Scaling factor (e.g., 1.5)",
        "scaling_method": "llm_natural_language",
        "serving_detection": "How serving size was determined",
        "unit_conversions": ["List of unit conversions made"]
    }}
}}

If scaling fails, return:
{{
    "success": false,
    "error": "Error description",
    "original_recipe": {json.dumps(recipe)}
}}

Return ONLY the JSON, no other text or explanation."""

        try:
            response = self.client.chat.completions.create(
                model="qwen/qwen3-4b-2507",
                messages=[
                    {"role": "system", "content": "You are a recipe scaling expert. Scale recipes intelligently and return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.1
            )
            
            # Parse the LLM response
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            try:
                # Find JSON in the response (in case there's extra text)
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    scaled_data = json.loads(json_str)
                    return scaled_data
                else:
                    raise ValueError("No JSON found in response")
                    
            except (json.JSONDecodeError, ValueError) as e:
                return {
                    "success": False,
                    "error": f"Failed to parse LLM response as JSON: {str(e)}",
                    "original_recipe": recipe,
                    "raw_response": response_text[:500]  # Include first 500 chars for debugging
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"LLM scaling failed: {str(e)}",
                "original_recipe": recipe
            }
    
    def _format_recipe_for_llm(self, recipe: dict) -> str:
        """
        Format recipe data for LLM processing.
        
        Args:
            recipe (dict): Recipe data
            
        Returns:
            str: Formatted recipe text
        """
        lines = []
        
        # Title and basic info
        lines.append(f"Title: {recipe.get('title', 'Unknown Recipe')}")
        lines.append(f"Servings: {recipe.get('servings', 'Unknown')}")
        lines.append(f"Prep Time: {recipe.get('prep_time', 'Unknown')}")
        lines.append(f"Cook Time: {recipe.get('cook_time', 'Unknown')}")
        lines.append(f"Total Time: {recipe.get('total_time', 'Unknown')}")
        lines.append("")
        
        # Ingredients
        lines.append("INGREDIENTS:")
        if 'ingredients' in recipe:
            for ingredient in recipe['ingredients']:
                if isinstance(ingredient, dict):
                    lines.append(f"- {ingredient.get('ingredient', 'Unknown ingredient')}")
                else:
                    lines.append(f"- {ingredient}")
        lines.append("")
        
        # Instructions
        lines.append("INSTRUCTIONS:")
        if 'instructions' in recipe:
            for instruction in recipe['instructions']:
                if isinstance(instruction, dict):
                    step_num = instruction.get('step', '?')
                    instruction_text = instruction.get('instruction', 'Unknown instruction')
                    lines.append(f"{step_num}. {instruction_text}")
                else:
                    lines.append(f"- {instruction}")
        
        return "\n".join(lines)
