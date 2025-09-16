#!/usr/bin/env python3.11
"""
LLM-First Recipe Extraction Tool

This tool uses the LLM's natural language understanding to extract recipe information
from HTML content, eliminating the need for complex deterministic parsing.
"""

from smolagents import Tool
import requests
from bs4 import BeautifulSoup
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


class RecipeExtractionLLMTool(Tool):
    """
    LLM-powered recipe extraction tool that uses natural language understanding
    to extract recipe information from any HTML structure.
    
    Telemetry Tracking:
    - extraction.url: Recipe URL being extracted
    - extraction.ingredients_count: Number of ingredients found
    - extraction.instructions_count: Number of instruction steps
    - extraction.servings: Recipe serving size
    - extraction.prep_time: Preparation time
    - extraction.cook_time: Cooking time
    - extraction.dietary_tags: Detected dietary tags
    - extraction.success_rate: Extraction success percentage
    """
    
    name: str = "recipe_extraction_llm"
    description: str = (
        "Extracts recipe information from a URL using LLM natural language understanding. "
        "Returns structured recipe data including ingredients, instructions, timing, and metadata. "
        "Much more flexible than deterministic parsing approaches."
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
        "url": {
            "type": "string", 
            "description": "The URL of the recipe to extract"
        }
    }
    
    def forward(self, url: str) -> str:
        """
        Extract recipe information from a URL using LLM.
        
        Args:
            url (str): The URL to extract recipe from
            
        Returns:
            str: JSON string with recipe data or error information
        """
        # Validate URL
        if not url or not url.strip():
            return json.dumps({
                "success": False,
                "error": "Empty or invalid URL provided",
                "url": url
            })
        
        if not url.startswith(('http://', 'https://')):
            return json.dumps({
                "success": False,
                "error": "Invalid URL format - must start with http:// or https://",
                "url": url
            })
        
        try:
            # Fetch the webpage
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Clean up the HTML content for LLM processing
            html_content = self._clean_html_for_llm(soup)
            
            # Use LLM to extract recipe information
            recipe_data = self._extract_with_llm(html_content, url)
            
            return json.dumps(recipe_data)
            
        except requests.RequestException as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to fetch URL: {str(e)}",
                "url": url
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "url": url
            })
    
    def _clean_html_for_llm(self, soup: BeautifulSoup) -> str:
        """
        Clean HTML content to make it more suitable for LLM processing.
        
        Args:
            soup (BeautifulSoup): Parsed HTML soup
            
        Returns:
            str: Cleaned HTML content
        """
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text content with some structure preserved
        text_content = soup.get_text(separator='\n', strip=True)
        
        # Limit content length to avoid token limits (keep first 6000 chars)
        if len(text_content) > 6000:
            text_content = text_content[:6000] + "..."
        
        return text_content
    
    def _extract_with_llm(self, content: str, url: str) -> dict:
        """
        Use LLM to extract recipe information from content.
        
        Args:
            content (str): Cleaned HTML/text content
            url (str): Original URL
            
        Returns:
            dict: Extracted recipe data
        """
        prompt = f"""Extract recipe information from this webpage content and return ONLY valid JSON.

Webpage content:
{content}

Return a JSON object with this exact structure:
{{
    "success": true,
    "url": "{url}",
    "recipe": {{
        "title": "Recipe title here",
        "description": "Recipe description if available",
        "url": "{url}",
        "ingredients": [
            {{"ingredient": "1 cup flour", "amount": "1", "unit": "cup"}},
            {{"ingredient": "2 eggs", "amount": "2", "unit": "each"}}
        ],
        "instructions": [
            {{"step": 1, "instruction": "First cooking step"}},
            {{"step": 2, "instruction": "Second cooking step"}}
        ],
        "prep_time": "10 minutes",
        "cook_time": "20 minutes", 
        "total_time": "30 minutes",
        "servings": "4",
        "dietary_tags": ["vegan", "gluten-free"],
        "difficulty": "easy",
        "source": "website name"
    }},
    "extraction_metadata": {{
        "timestamp": {int(time.time())},
        "source_domain": "{url.split('/')[2] if len(url.split('/')) > 2 else 'unknown'}",
        "extraction_method": "llm_natural_language"
    }}
}}

If no recipe is found or content is not a recipe, return:
{{
    "success": false,
    "error": "No recipe found in content",
    "url": "{url}"
}}

Return ONLY the JSON, no other text or explanation."""

        try:
            response = self.client.chat.completions.create(
                model="qwen/qwen3-4b-2507",
                messages=[
                    {"role": "system", "content": "You are a recipe extraction expert. Extract recipe information and return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
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
                    recipe_data = json.loads(json_str)
                    return recipe_data
                else:
                    raise ValueError("No JSON found in response")
                    
            except (json.JSONDecodeError, ValueError) as e:
                return {
                    "success": False,
                    "error": f"Failed to parse LLM response as JSON: {str(e)}",
                    "url": url,
                    "raw_response": response_text[:500]  # Include first 500 chars for debugging
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"LLM extraction failed: {str(e)}",
                "url": url
            }
