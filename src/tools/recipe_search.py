#!/usr/bin/env python3.11
"""
Recipe Search & Extraction Tool

This tool searches for recipes with dietary restrictions and extracts recipe content
from web search results using duckduckgo-search and web scraping.
"""

from smolagents import Tool
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
import json
import time


class RecipeSearchTool(Tool):
    """
    Tool for searching and extracting recipes with dietary filtering.
    
    This tool:
    - Searches for recipes using duckduckgo-search
    - Extracts recipe content from web pages
    - Returns formatted recipe data
    - Handles errors gracefully
    """
    
    name: str = "recipe_search"
    description: str = (
        "Searches for recipes with dietary restrictions and extracts recipe content. "
        "Returns structured recipe data including ingredients, instructions, and metadata. "
        "The agent should format the response as: 'RECIPE_FOUND: [title] | URL: [url] | DESCRIPTION: [description]' "
        "or 'NO_RECIPES_FOUND: [error message]' for validation purposes."
    )
    
    def __init__(self):
        super().__init__()
        self._search_cache = {}  # Cache search results to ensure consistency
    
    inputs: dict = {
        "query": {
            "type": "string", 
            "description": "The recipe search query (e.g., 'pancakes', 'bread')"
        },
        "dietary_restrictions": {
            "type": "array",
            "description": "List of dietary restrictions (e.g., ['vegan', 'gluten-free', 'keto'])",
            "items": {"type": "string"},
            "nullable": True
        }
    }
    
    output_type: dict = "string"

    def forward(self, query: str, dietary_restrictions: list = None) -> str:
        """
        Search for recipes and extract content from web results.
        
        Args:
            query (str): The recipe search query (e.g., 'pancakes', 'bread')
            dietary_restrictions (list): List of dietary restrictions (e.g., ['vegan', 'gluten-free'])
            
        Returns:
            str: JSON string containing recipe data or error information
            
        Raises:
            ValueError: If query is empty or invalid
            ConnectionError: If search service is unavailable
            
        Example:
            >>> tool = RecipeSearchTool()
            >>> result = tool.forward("vegan pancakes")
            >>> data = json.loads(result)
            >>> print(data["success"])
            True
        """
        # Validate input
        if not query or not query.strip():
            return json.dumps({
                "error": "Empty or invalid query",
                "query": query or "",
                "suggestions": ["Provide a valid search term", "Try 'vegan pancakes' or 'gluten-free bread'"]
            })
        
        # Limit query length to prevent abuse
        if len(query) > 200:
            return json.dumps({
                "error": "Query too long",
                "query": query[:50] + "...",
                "suggestions": ["Use shorter search terms", "Maximum 200 characters allowed"]
            })
        
        try:
            # Improve search query by ensuring "recipe" is included and adding dietary restrictions
            # This will also validate the query quality
            improved_query = self._improve_search_query(query.strip(), dietary_restrictions)
            
            # Search for recipes
            search_results = self._search_recipes(improved_query)
            
            if not search_results:
                return json.dumps({
                    "error": "No recipes found",
                    "query": query,
                    "suggestions": [
                        "Try a different search term",
                        "Check spelling",
                        "Use more general terms (e.g., 'pancakes' instead of 'fluffy vegan banana oat pancakes')"
                    ]
                })
            
            # Extract recipe content from all results
            recipes_data = []
            for result in search_results:
                recipe_data = self._extract_recipe_content(result)
                # Only include recipes that don't have extraction errors
                if "error" not in recipe_data:
                    recipes_data.append(recipe_data)
            
            # If no valid recipes found, return error
            if not recipes_data:
                return json.dumps({
                    "error": "No valid recipes found",
                    "query": query,
                    "suggestions": ["Try a different search term", "Check if recipe sites are accessible"]
                })
            
            return json.dumps({
                "success": True,
                "query": query,
                "recipes": recipes_data,  # Return all valid recipes
                "search_metadata": {
                    "total_results": len(recipes_data),
                    "timestamp": time.time(),
                    "search_engine": "duckduckgo"
                }
            })
            
        except ValueError as e:
            # Handle query validation errors
            return json.dumps({
                "error": f"Invalid query: {str(e)}",
                "query": query,
                "suggestions": ["Provide a valid recipe search term", "Try 'chocolate cake' or 'vegan pancakes'"]
            })
        except ConnectionError as e:
            return json.dumps({
                "error": f"Search service unavailable: {str(e)}",
                "query": query,
                "suggestions": ["Check internet connection", "Try again later"]
            })
        except Exception as e:
            return json.dumps({
                "error": f"Unexpected error: {str(e)}",
                "query": query,
                "suggestions": ["Try a different search term", "Contact support if issue persists"]
            })
    
    def _improve_search_query(self, query: str, dietary_restrictions: list = None) -> str:
        """
        Improve the search query by ensuring 'recipe' is included and adding dietary restrictions.
        Also validates that the query is reasonable for recipe searching.
        
        Args:
            query (str): The original search query
            dietary_restrictions (list): List of dietary restrictions to include
            
        Returns:
            str: Improved query with 'recipe' and dietary restrictions appended
            
        Raises:
            ValueError: If query is empty, too short, or contains only non-alphabetic characters
        """
        query_lower = query.lower().strip()
        
        # Validate query quality
        if not query_lower:
            raise ValueError("Empty query")
        
        # Check if query is too short (less than 2 characters)
        if len(query_lower) < 2:
            raise ValueError("Query too short")
        
        # Check if query contains only non-alphabetic characters (numbers, symbols, etc.)
        if not any(c.isalpha() for c in query_lower):
            raise ValueError("Query contains no alphabetic characters")
        
        # Check if query looks like nonsense (contains random numbers/characters)
        if len(query_lower) > 8:
            # Check for patterns that suggest nonsense
            has_numbers = any(c.isdigit() for c in query_lower)
            has_food_words = any(word in query_lower for word in [
                'cake', 'bread', 'soup', 'pasta', 'pizza', 'salad', 'chicken', 'beef', 'fish', 
                'vegan', 'keto', 'gluten', 'dairy', 'free', 'healthy', 'easy', 'quick', 'simple',
                'cookies', 'muffins', 'pancakes', 'waffles', 'smoothie', 'sauce', 'dressing'
            ])
            
            # If it has numbers but no food words, it's likely nonsense
            if has_numbers and not has_food_words:
                raise ValueError("Query appears to be nonsensical")
            
            # If it's mostly non-alphabetic characters, it's likely nonsense
            alpha_ratio = sum(c.isalpha() for c in query_lower) / len(query_lower)
            if alpha_ratio < 0.6 and not has_food_words:
                raise ValueError("Query appears to be nonsensical")
        
        # Build the enhanced query with dietary restrictions and recipe
        enhanced_query = query
        
        # Add dietary restrictions if provided
        if dietary_restrictions:
            # Filter out any restrictions that are already in the query
            restrictions_to_add = []
            for restriction in dietary_restrictions:
                if restriction.lower() not in query_lower:
                    restrictions_to_add.append(restriction)
            
            if restrictions_to_add:
                enhanced_query = f"{' '.join(restrictions_to_add)} {enhanced_query}"
        
        # Add 'recipe' if not already present
        if 'recipe' not in query_lower:
            enhanced_query = f"{enhanced_query} recipe"
        
        return enhanced_query
    
    def _search_recipes(self, query: str) -> list:
        """
        Search for recipes using duckduckgo-search.
        
        Args:
            query (str): The search query (already validated and cleaned)
            
        Returns:
            list: List of search result dictionaries with 'href', 'title', and 'body' keys
            
        Note:
            This method targets specific recipe websites for better quality results.
            If the search fails, an empty list is returned.
            Results are cached to ensure consistency across multiple calls.
        """
        # Check cache first to ensure consistent results
        if query in self._search_cache:
            return self._search_cache[query]
        
        try:
            with DDGS() as ddgs:
                # Search for recipes using natural DuckDuckGo results
                # Note: query already has 'recipe' appended if needed by _improve_search_query
                results = list(ddgs.text(query, max_results=10))
                
                # Filter out known problematic sites and prioritize working ones
                filtered_results = []
                blocked_domains = ['foodnetwork.com']  # Sites that consistently block our requests
                roundup_keywords = ['roundup', 'collection', 'best', 'top', 'list', 'guide', 'favorite', 'delicious', 'scrumptious', 'easy', 'simple']  # Avoid recipe roundup pages
                
                for result in results:
                    url = result.get('href', '')
                    title = result.get('title', '').lower()
                    
                    # Skip blocked domains
                    if any(domain in url for domain in blocked_domains):
                        continue
                    
                    # Skip recipe roundup/collection pages (they don't have single recipes)
                    if any(keyword in title for keyword in roundup_keywords):
                        continue
                    
                    # Prioritize known working recipe sites
                    if any(domain in url for domain in ['allrecipes.com', 'epicurious.com', 'bonappetit.com', 'tasty.co', 'delish.com']):
                        filtered_results.append(result)
                    else:
                        # Include other recipe sites as fallback
                        if any(keyword in url.lower() for keyword in ['recipe', 'cooking', 'food']):
                            filtered_results.append(result)
                
                # Take up to 5 results
                results = filtered_results[:5]
                
                # Cache the results to ensure consistency
                self._search_cache[query] = results
                return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def _extract_recipe_content(self, search_result: dict) -> dict:
        """
        Extract recipe content from a web page search result.
        
        Args:
            search_result (dict): Dictionary containing URL, title, and body from search
                Expected keys: 'href', 'title', 'body'
            
        Returns:
            dict: Dictionary containing extracted recipe data with keys:
                - id (str): Unique recipe identifier
                - title (str): Cleaned recipe title
                - url (str): Recipe URL
                - description (str): Cleaned description
                - source (str): Website source name
                - extraction_status (str): Current extraction status
                - ready_for_extraction (bool): Whether ready for full extraction
                
        Note:
            Currently extracts only basic metadata. Full recipe content extraction
            will be implemented in Tool 2 (Recipe Extraction Tool).
        """
        try:
            url = search_result.get('href', '')
            title = search_result.get('title', '')
            body = search_result.get('body', '')
            
            # Validate required fields
            if not url:
                return {
                    "error": "No URL found in search result",
                    "title": title or "Unknown",
                    "url": "",
                    "extraction_status": "failed"
                }
            
            # Clean up the title - take only the first part before "|" or " - "
            clean_title = title.split('|')[0].split(' - ')[0].strip()
            if not clean_title:
                clean_title = "Untitled Recipe"
            
            # Clean up the description - take first sentence
            clean_description = body.split('.')[0] + '.' if body else "Recipe description not available"
            
            return {
                "id": f"recipe_{hash(url)}",  # Unique identifier
                "title": clean_title,
                "url": url,
                "description": clean_description,
                "source": self._extract_source(url),
                "extraction_status": "url_only",  # Will be "complete" when we add full scraping
                "ready_for_extraction": True
            }
            
        except Exception as e:
            return {
                "error": f"Content extraction failed: {str(e)}",
                "title": search_result.get('title', 'Unknown'),
                "url": search_result.get('href', ''),
                "extraction_status": "failed"
            }
    
    def _extract_source(self, url: str) -> str:
        """
        Extract the source website name from URL.
        
        Args:
            url (str): The recipe URL
            
        Returns:
            str: Source website name (e.g., 'AllRecipes', 'Food Network', 'Bon Appétit')
                Returns 'Unknown' if source cannot be determined
        """
        try:
            if 'allrecipes.com' in url:
                return 'AllRecipes'
            elif 'foodnetwork.com' in url:
                return 'Food Network'
            elif 'bonappetit.com' in url:
                return 'Bon Appétit'
            elif 'epicurious.com' in url:
                return 'Epicurious'
            else:
                return 'Unknown'
        except:
            return 'Unknown'
