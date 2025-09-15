#!/usr/bin/env python3.11
"""
Recipe Extraction Tool

This tool extracts detailed recipe information from web pages using web scraping
and structured data parsing. It converts recipe URLs into structured JSON data.
"""

from smolagents import Tool
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urlparse


class RecipeExtractionTool(Tool):
    """
    Tool for extracting detailed recipe information from web pages.
    
    This tool:
    - Scrapes recipe web pages for structured data
    - Extracts ingredients, instructions, timing, and metadata
    - Returns formatted recipe data as JSON
    - Handles various recipe website formats
    """
    
    name: str = "recipe_extraction"
    description: str = (
        "Extracts detailed recipe information from a recipe URL. "
        "Returns structured recipe data including ingredients, instructions, timing, and metadata. "
        "The agent should format the response as: 'RECIPE_EXTRACTED: [title] | INGREDIENTS: [count] | STEPS: [count] | TIME: [total_time]' "
        "or 'EXTRACTION_FAILED: [error message]' for validation purposes."
    )
    
    inputs: dict = {
        "url": {
            "type": "string", 
            "description": "The recipe URL to extract from (e.g., 'https://www.allrecipes.com/recipe/191885/vegan-pancakes/')"
        }
    }
    
    output_type: dict = "string"

    def forward(self, url: str) -> str:
        """
        Extract recipe information from a web page URL.
        
        Args:
            url (str): The recipe URL to extract from
            
        Returns:
            str: JSON string containing extracted recipe data or error information
        """
        
        # Validate URL
        if not url or not url.strip():
            return json.dumps({
                "error": "Empty or invalid URL",
                "url": url,
                "suggestions": ["Provide a valid recipe URL", "URL should start with http:// or https://"]
            })
        
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            return json.dumps({
                "error": "Invalid URL format",
                "url": url,
                "suggestions": ["URL must start with http:// or https://"]
            })
        
        try:
            # Extract recipe data
            recipe_data = self._extract_recipe_data(url)
            
            if recipe_data.get("error"):
                return json.dumps(recipe_data)
            
            return json.dumps({
                "success": True,
                "url": url,
                "recipe": recipe_data,
                "extraction_metadata": {
                    "timestamp": time.time(),
                    "source_domain": urlparse(url).netloc,
                    "extraction_method": "web_scraping"
                }
            })
            
        except Exception as e:
            return json.dumps({
                "error": f"Extraction failed: {str(e)}",
                "url": url,
                "suggestions": ["Check if URL is accessible", "Try a different recipe URL"]
            })
    
    def _extract_recipe_data(self, url: str) -> dict:
        """
        Extract recipe data from a web page.
        
        Args:
            url (str): The recipe URL
            
        Returns:
            dict: Extracted recipe data
        """
        try:
            # Fetch the web page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to extract structured data (JSON-LD)
            recipe_data = self._extract_structured_data(soup)
            
            if not recipe_data:
                # Fallback to HTML parsing
                recipe_data = self._extract_from_html(soup, url)
            
            return recipe_data
            
        except requests.RequestException as e:
            return {"error": f"Failed to fetch URL: {str(e)}"}
        except Exception as e:
            return {"error": f"Parsing error: {str(e)}"}
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> dict:
        """
        Extract recipe data from JSON-LD structured data.
        
        Args:
            soup (BeautifulSoup): Parsed HTML soup
            
        Returns:
            dict: Extracted recipe data or None if not found
        """
        try:
            # Look for JSON-LD script tags
            json_scripts = soup.find_all('script', type='application/ld+json')
            
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    
                    # Handle arrays of structured data
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') == 'Recipe':
                                return self._parse_recipe_schema(item)
                    elif data.get('@type') == 'Recipe':
                        return self._parse_recipe_schema(data)
                        
                except json.JSONDecodeError:
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _parse_recipe_schema(self, schema_data: dict) -> dict:
        """
        Parse Recipe schema.org structured data.
        
        Args:
            schema_data (dict): Recipe schema data
            
        Returns:
            dict: Parsed recipe data
        """
        recipe = {
            "title": schema_data.get("name", ""),
            "description": schema_data.get("description", ""),
            "url": schema_data.get("url", ""),
            "ingredients": [],
            "instructions": [],
            "prep_time": "",
            "cook_time": "",
            "total_time": "",
            "servings": "",
            "dietary_tags": [],
            "difficulty": "",
            "source": ""
        }
        
        # Extract ingredients
        ingredients = schema_data.get("recipeIngredient", [])
        for ingredient in ingredients:
            if isinstance(ingredient, str):
                recipe["ingredients"].append({
                    "raw_text": ingredient,
                    "amount": "",
                    "unit": "",
                    "ingredient": ingredient
                })
        
        # Extract instructions
        instructions = schema_data.get("recipeInstructions", [])
        for i, instruction in enumerate(instructions, 1):
            if isinstance(instruction, str):
                recipe["instructions"].append({
                    "step": i,
                    "instruction": instruction
                })
            elif isinstance(instruction, dict):
                text = instruction.get("text", instruction.get("name", ""))
                if text:
                    recipe["instructions"].append({
                        "step": i,
                        "instruction": text
                    })
        
        # Extract timing
        recipe["prep_time"] = schema_data.get("prepTime", "")
        recipe["cook_time"] = schema_data.get("cookTime", "")
        recipe["total_time"] = schema_data.get("totalTime", "")
        
        # Extract servings
        recipe_yield = schema_data.get("recipeYield", "")
        if isinstance(recipe_yield, (str, int)):
            recipe["servings"] = str(recipe_yield)
        
        # Extract dietary information
        recipe_category = schema_data.get("recipeCategory", [])
        if isinstance(recipe_category, str):
            recipe_category = [recipe_category]
        
        for category in recipe_category:
            if category.lower() in ["vegan", "vegetarian", "gluten-free", "keto", "paleo", "dairy-free"]:
                recipe["dietary_tags"].append(category.lower())
        
        return recipe
    
    def _extract_from_html(self, soup: BeautifulSoup, url: str) -> dict:
        """
        Generic HTML parsing for recipe data that works across different sites.
        Uses flexible selectors and heuristics to extract recipe information.
        
        Args:
            soup (BeautifulSoup): Parsed HTML soup
            url (str): Original URL
            
        Returns:
            dict: Extracted recipe data
        """
        recipe = {
            "title": "",
            "description": "",
            "url": url,
            "ingredients": [],
            "instructions": [],
            "prep_time": "",
            "cook_time": "",
            "total_time": "",
            "servings": "",
            "dietary_tags": [],
            "difficulty": "",
            "source": urlparse(url).netloc
        }
        
        # Extract title - try multiple approaches
        title_elem = soup.find('h1')
        if not title_elem:
            # Try other common title selectors
            title_elem = soup.select_one('h1, .recipe-title, .recipe-name, [class*="title"]')
        
        if title_elem:
            recipe["title"] = title_elem.get_text().strip()
        
        # Extract ingredients using flexible approach
        self._extract_ingredients_flexible(soup, recipe)
        
        # Extract instructions using flexible approach
        self._extract_instructions_flexible(soup, recipe)
        
        # Extract timing information
        self._extract_timing_info(soup, recipe)
        
        # Extract servings
        self._extract_servings(soup, recipe)
        
        return recipe
    
    def _extract_ingredients_flexible(self, soup: BeautifulSoup, recipe: dict):
        """Extract ingredients using flexible selectors and heuristics."""
        # Try multiple ingredient selectors
        ingredient_selectors = [
            '[itemprop="recipeIngredient"]',
            '.recipe-ingredients li',
            '.ingredients li',
            '.ingredient-item',
            '.recipe-ingredient',
            '[class*="ingredient"] li',
            'li[class*="ingredient"]'
        ]
        
        for selector in ingredient_selectors:
            ingredients = soup.select(selector)
            if ingredients and len(ingredients) > 2:  # Need at least 3 ingredients to be confident
                for ingredient in ingredients:
                    text = ingredient.get_text().strip()
                    if self._is_valid_ingredient(text):
                        recipe["ingredients"].append({
                            "raw_text": text,
                            "amount": "",
                            "unit": "",
                            "ingredient": text
                        })
                if len(recipe["ingredients"]) > 2:
                    return  # Found good ingredients, stop looking
    
    def _extract_instructions_flexible(self, soup: BeautifulSoup, recipe: dict):
        """Extract instructions using flexible selectors and heuristics."""
        # Try multiple instruction selectors
        instruction_selectors = [
            '[itemprop="recipeInstructions"]',
            '.recipe-instructions li',
            '.instructions li',
            '.instruction-item',
            '.recipe-step',
            '[class*="instruction"] li',
            '[class*="direction"] li',
            'li[class*="step"]'
        ]
        
        for selector in instruction_selectors:
            instructions = soup.select(selector)
            if instructions and len(instructions) > 0:
                for i, instruction in enumerate(instructions, 1):
                    text = instruction.get_text().strip()
                    if self._is_valid_instruction(text):
                        recipe["instructions"].append({
                            "step": i,
                            "instruction": text
                        })
                if len(recipe["instructions"]) > 0:
                    return  # Found good instructions, stop looking
    
    def _extract_timing_info(self, soup: BeautifulSoup, recipe: dict):
        """Extract timing information using flexible approach."""
        # Look for common timing patterns
        timing_text = soup.get_text()
        
        # Common timing patterns
        import re
        
        # Prep time patterns
        prep_patterns = [
            r'prep.*?(\d+)\s*(?:min|minutes?|hr|hours?)',
            r'preparation.*?(\d+)\s*(?:min|minutes?|hr|hours?)',
            r'(\d+)\s*(?:min|minutes?|hr|hours?)\s*prep'
        ]
        
        for pattern in prep_patterns:
            match = re.search(pattern, timing_text, re.IGNORECASE)
            if match:
                recipe["prep_time"] = match.group(1) + " minutes"
                break
        
        # Cook time patterns
        cook_patterns = [
            r'cook.*?(\d+)\s*(?:min|minutes?|hr|hours?)',
            r'cooking.*?(\d+)\s*(?:min|minutes?|hr|hours?)',
            r'(\d+)\s*(?:min|minutes?|hr|hours?)\s*cook'
        ]
        
        for pattern in cook_patterns:
            match = re.search(pattern, timing_text, re.IGNORECASE)
            if match:
                recipe["cook_time"] = match.group(1) + " minutes"
                break
    
    def _extract_servings(self, soup: BeautifulSoup, recipe: dict):
        """Extract serving information using flexible approach."""
        serving_text = soup.get_text()
        
        # Common serving patterns
        import re
        serving_patterns = [
            r'serves?\s*(\d+)',
            r'(\d+)\s*servings?',
            r'yields?\s*(\d+)',
            r'makes?\s*(\d+)'
        ]
        
        for pattern in serving_patterns:
            match = re.search(pattern, serving_text, re.IGNORECASE)
            if match:
                recipe["servings"] = match.group(1)
                break
    
    def _is_valid_ingredient(self, text: str) -> bool:
        """Check if text looks like a valid ingredient."""
        if not text or len(text) < 3:
            return False
        
        # Skip common non-ingredient text
        skip_words = [
            'ingredients', 'directions', 'instructions', 'steps',
            'cook mode', 'keep screen awake', 'oops', 'something went wrong',
            'our team is working', 'recipe was developed', 'ingredient amounts',
            'cooking times', 'note that not all', 'original recipe', 'yields'
        ]
        
        text_lower = text.lower()
        return not any(skip in text_lower for skip in skip_words)
    
    def _is_valid_instruction(self, text: str) -> bool:
        """Check if text looks like a valid instruction."""
        if not text or len(text) < 10:
            return False
        
        # Skip common non-instruction text
        skip_words = [
            'directions', 'instructions', 'steps', 'dotdash meredith',
            'editor\'s note', 'electric griddles', 'food studios'
        ]
        
        text_lower = text.lower()
        return not any(skip in text_lower for skip in skip_words)
