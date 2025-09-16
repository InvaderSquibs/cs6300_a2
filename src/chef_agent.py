#!/usr/bin/env python3.11
"""
AI Chef Assistant Agent

A multi-tooled agent that helps with recipe curation and modification.
Uses smolagents framework with specialized tools for recipe management.

Usage:
    python3.11 chef_agent.py                    # Run interactive mode
    python3.11 chef_agent.py help               # Show help and available tools
    python3.11 chef_agent.py search "query"     # Search for recipes
    python3.11 chef_agent.py test               # Run connection test
"""

from smolagents import CodeAgent, Tool
from smolagents import OpenAIServerModel
import dotenv
import os
import sys
import json

# Import our custom tools
from tools.recipe_search import RecipeSearchTool
from tools.recipe_extraction_llm import RecipeExtractionLLMTool
from tools.recipe_scaling_llm import RecipeScalingLLMTool

# Load environment variables
dotenv.load_dotenv()


def create_chef_agent():
    """
    Creates and configures the AI Chef Assistant agent with all tools.
    
    Returns:
        CodeAgent: Configured agent ready for recipe tasks
    """
    
    # Initialize tools
    recipe_search_tool = RecipeSearchTool()
    recipe_extraction_tool = RecipeExtractionLLMTool()
    recipe_scaling_tool = RecipeScalingLLMTool()
    # recipe_validation_tool = RecipeValidationTool()
    
    tools = [recipe_search_tool, recipe_extraction_tool, recipe_scaling_tool]
    
    # Configure the model
    model = OpenAIServerModel(
        model_id=os.getenv("MODEL_ID", "google/gemma-3-27b"),
        api_base=os.getenv("GPT_ENDPOINT", "http://192.168.1.27:1234/v1"),
        api_key=os.getenv("GEMINI_API_KEY", ""),
    )
    
    # Create the agent
    agent = CodeAgent(
        tools=tools,
        model=model,
        additional_authorized_imports=['json'],
        max_steps=3  # Reduce steps to prevent loops
    )
    
    return agent


def show_help():
    """
    Display help information and available tools.
    """
    print("🧑‍🍳 AI Chef Assistant - Help & Usage")
    print("=" * 50)
    print()
    print("USAGE:")
    print("  python3.11 chef_agent.py                    # Interactive mode")
    print("  python3.11 chef_agent.py help               # Show this help")
    print()
    print("NATURAL LANGUAGE REQUESTS:")
    print("  python3.11 chef_agent.py \"I'd like some pancakes please\"")
    print("  python3.11 chef_agent.py \"I'd like some pancakes please\" --restrictions vegan,keto")
    print("  python3.11 chef_agent.py \"Find me a chocolate cake recipe\" --restrictions gluten-free")
    print()
    print("LEGACY COMMANDS:")
    print("  python3.11 chef_agent.py search \"query\"     # Search for recipes")
    print("  python3.11 chef_agent.py search \"query\" --diet \"restrictions\"  # Search with dietary restrictions")
    print("  python3.11 chef_agent.py extract \"url\"      # Extract recipe from URL")
    print("  python3.11 chef_agent.py test               # Test connection")
    print("  python3.11 chef_agent.py e2e                # End-to-end test (basic pancakes)")
    print("  python3.11 chef_agent.py e2e --diet \"restrictions\"  # End-to-end test with dietary restrictions")
    print("  python3.11 chef_agent.py tools              # Tool-by-tool test with JSON outputs")
    print("  python3.11 chef_agent.py tools --diet \"restrictions\"  # Tool-by-tool test with dietary restrictions")
    print()
    print("AVAILABLE TOOLS:")
    print("=" * 20)
    
    # Show tool information
    try:
        # Create tools directly instead of through agent
        recipe_search_tool = RecipeSearchTool()
        recipe_extraction_tool = RecipeExtractionLLMTool()
        tools = [recipe_search_tool, recipe_extraction_tool, recipe_scaling_tool]
        
        for tool in tools:
            print(f"🔧 {tool.name}")
            print(f"   Description: {tool.description}")
            print(f"   Inputs: {list(tool.inputs.keys())}")
            print()
    except Exception as e:
        print(f"❌ Error loading tools: {e}")
        print()
    
    print("EXAMPLES:")
    print("=" * 10)
    print('  python3.11 chef_agent.py "I\'d like some pancakes please"')
    print('  python3.11 chef_agent.py "I\'d like some pancakes please" --restrictions vegan,gluten-free')
    print('  python3.11 chef_agent.py "Find me a bread recipe" --restrictions keto')
    print('  python3.11 chef_agent.py "I want to make cookies" --restrictions paleo,dairy-free')
    print('  python3.11 chef_agent.py "What can I make for dinner?" --restrictions vegetarian')
    print()
    print("LEGACY EXAMPLES:")
    print('  python3.11 chef_agent.py search "pancakes"')
    print('  python3.11 chef_agent.py search "pancakes" --diet "vegan,gluten-free"')
    print('  python3.11 chef_agent.py extract "https://www.allrecipes.com/recipe/191885/vegan-pancakes/"')
    print()
    print("SUPPORTED DIETARY RESTRICTIONS:")
    print("=" * 35)
    print("  vegan, vegetarian, keto, paleo, gluten-free, dairy-free,")
    print("  nut-free, soy-free, sugar-free, low-carb, high-protein")
    print()
    print("ENVIRONMENT:")
    print("=" * 12)
    print("  Make sure your .env file contains:")
    print("  - GPT_ENDPOINT (your LLM endpoint)")
    print("  - MODEL_ID (model identifier)")
    print("  - GEMINI_API_KEY (if using Gemini)")


def run_search(query, dietary_restrictions=None):
    """
    Run a recipe search with the given query and dietary restrictions.
    
    Args:
        query (str): The search query
        dietary_restrictions (list): List of dietary restrictions (e.g., ['vegan', 'gluten-free'])
    """
    print(f"🔍 Searching for: {query}")
    if dietary_restrictions:
        print(f"🥗 Dietary restrictions: {', '.join(dietary_restrictions)}")
    print("=" * 50)
    
    try:
        agent = create_chef_agent()
        
        # Build the search prompt with dietary restrictions
        search_prompt = f"Search for '{query}' using the recipe_search tool"
        if dietary_restrictions:
            restrictions_str = ', '.join(dietary_restrictions)
            search_prompt += f" with dietary restrictions: {restrictions_str}"
        
        search_prompt += ". The tool returns a JSON string - use json.loads() to parse it. If the JSON contains an 'error' field, return 'NO_RECIPES_FOUND: [error message]'. If it contains a 'recipes' array with results, extract the recipe title, URL, and description from the first recipe. You MUST call final_answer() with the format: 'RECIPE_FOUND: [title] | URL: [url] | DESCRIPTION: [description]' or 'NO_RECIPES_FOUND: [error message]'. Do not stop until you call final_answer(). Use the exact query '{query}' - do not substitute it with something else."
        
        result = agent.run(search_prompt)
        
        print("📋 Search Results:")
        print(result)
            
    except Exception as e:
        print(f"❌ Search failed: {e}")
        import traceback
        traceback.print_exc()


def run_extraction(url):
    """
    Run recipe extraction with the given URL.
    
    Args:
        url (str): The recipe URL to extract from
    """
    print(f"🔍 Extracting recipe from: {url}")
    print("=" * 50)
    
    try:
        agent = create_chef_agent()
        
        # Build the extraction prompt
        extraction_prompt = f"Extract recipe information from the URL '{url}' using the recipe_extraction tool. The tool returns a JSON string - use json.loads() to parse it. If the JSON contains an 'error' field, return 'EXTRACTION_FAILED: [error message]'. If it contains a 'recipe' object, extract the title, ingredient count, instruction count, and total time. Use the correct field names: data['recipe']['title'], data['recipe']['ingredients'], data['recipe']['instructions'], data['recipe']['prep_time'], data['recipe']['cook_time']. You MUST call final_answer() with the format: 'RECIPE_EXTRACTED: [title] | INGREDIENTS: [count] | STEPS: [count] | TIME: [total_time]' or 'EXTRACTION_FAILED: [error message]'. Do not stop until you call final_answer()."
        
        result = agent.run(extraction_prompt)
        
        print("📋 Extraction Results:")
        print(result)
            
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()


def run_test():
    """
    Run connection test for the AI Chef Assistant.
    """
    print("🧑‍🍳 AI Chef Assistant - Connection Test")
    print("=" * 50)
    
    try:
        # Create the agent
        agent = create_chef_agent()
        
        # Test the recipe search tool
        print("Testing recipe search tool with 'vegan pancakes'...")
        answer = agent.run("Search for vegan pancakes using the recipe_search tool")
        print(f"Agent response: {answer}")
        
        print("\n✅ Tool connection test successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def run_end_to_end_test(dietary_restrictions=None):
    """
    Run a comprehensive end-to-end test simulating a real user request.
    
    Args:
        dietary_restrictions (list): List of dietary restrictions (e.g., ['vegan'])
    """
    print("🧑‍🍳 AI Chef Assistant - End-to-End Test")
    print("=" * 50)
    
    if dietary_restrictions:
        print(f"🥗 Dietary restrictions: {', '.join(dietary_restrictions)}")
    
    print("🎯 Simulating user request: 'I'd like some pancakes please'")
    print("=" * 50)
    
    try:
        agent = create_chef_agent()
        
        # Create a natural language prompt that should trigger the full pipeline
        if dietary_restrictions:
            restrictions_str = ', '.join(dietary_restrictions)
            user_prompt = f"I'd like some pancakes please. I have dietary restrictions: {restrictions_str}. Please find me a recipe and extract the full recipe details including ingredients and instructions."
        else:
            user_prompt = "I'd like some pancakes please. Please find me a recipe and extract the full recipe details including ingredients and instructions."
        
        print(f"🤖 Processing: {user_prompt}")
        print("=" * 50)
        
        # Run the agent with the natural language prompt
        result = agent.run(user_prompt)
        
        print("📋 Full Pipeline Results:")
        print("=" * 30)
        print(result)
        
        # Parse the result to validate it contains the expected elements
        print("\n🔍 Validation:")
        print("=" * 15)
        
        # Check if we got a structured recipe response
        if isinstance(result, dict) and 'title' in result and 'ingredients' in result and 'instructions' in result:
            print("✅ Recipe search successful")
            print("✅ Recipe extraction successful")
            print(f"✅ Recipe contains {len(result['ingredients'])} ingredients and {len(result['instructions'])} steps")
            print(f"✅ Recipe title: {result['title']}")
        elif "RECIPE_FOUND:" in str(result):
            print("✅ Recipe search successful (legacy format)")
        else:
            print("❌ Recipe search failed")
            
        if "RECIPE_EXTRACTED:" in str(result):
            print("✅ Recipe extraction successful (legacy format)")
        elif isinstance(result, dict) and 'ingredients' in result and 'instructions' in result:
            print("✅ Recipe extraction successful (structured format)")
        else:
            print("❌ Recipe extraction failed")
            
        if "INGREDIENTS:" in str(result) and "STEPS:" in str(result):
            print("✅ Recipe contains ingredients and steps (legacy format)")
        elif isinstance(result, dict) and 'ingredients' in result and 'instructions' in result:
            print("✅ Recipe contains ingredients and steps (structured format)")
        else:
            print("❌ Recipe missing ingredients or steps")
        
        print("\n✅ End-to-end test completed!")
        
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()


def run_end_to_end_test_with_tool_outputs(dietary_restrictions=None):
    """
    Run end-to-end test with detailed tool output inspection.
    
    Args:
        dietary_restrictions (list): List of dietary restrictions (e.g., ['vegan'])
    """
    print("🧑‍🍳 AI Chef Assistant - End-to-End Test (Tool Outputs)")
    print("=" * 60)
    
    if dietary_restrictions:
        print(f"🥗 Dietary restrictions: {', '.join(dietary_restrictions)}")
    
    print("🎯 Simulating user request: 'I'd like some pancakes please'")
    print("=" * 60)
    
    try:
        # Test Tool 1: Recipe Search
        print("\n🔍 TOOL 1: Recipe Search")
        print("-" * 30)
        
        from tools.recipe_search import RecipeSearchTool
        search_tool = RecipeSearchTool()
        
        if dietary_restrictions:
            search_result = search_tool.forward("pancakes", dietary_restrictions)
        else:
            search_result = search_tool.forward("pancakes")
        
        print("📋 Search Tool Output (JSON):")
        try:
            import json
            search_data = json.loads(search_result)
            print(json.dumps(search_data, indent=2))
            
            # Extract URL for next tool
            if search_data.get('success') and search_data.get('recipes'):
                recipe_url = search_data['recipes'][0]['url']
                print(f"\n🔗 Extracted URL: {recipe_url}")
            else:
                print("❌ No recipe URL found in search results")
                return
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse search JSON: {e}")
            print(f"Raw output: {search_result}")
            return
        
        # Test Tool 2: Recipe Extraction
        print("\n🔍 TOOL 2: Recipe Extraction")
        print("-" * 30)
        
        extraction_tool = RecipeExtractionLLMTool()
        
        extraction_result = extraction_tool.forward(recipe_url)
        
        print("📋 Extraction Tool Output (JSON):")
        try:
            extraction_data = json.loads(extraction_result)
            print(json.dumps(extraction_data, indent=2))
            
            # Extract key recipe information
            if extraction_data.get('success') and extraction_data.get('recipe'):
                recipe = extraction_data['recipe']
                print(f"\n📊 Recipe Summary:")
                print(f"  Title: {recipe.get('title', 'N/A')}")
                print(f"  Ingredients: {len(recipe.get('ingredients', []))} found")
                print(f"  Instructions: {len(recipe.get('instructions', []))} found")
                print(f"  Servings: {recipe.get('servings', 'N/A')}")
                print(f"  Cook Time: {recipe.get('cook_time', 'N/A')}")
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse extraction JSON: {e}")
            print(f"Raw output: {extraction_result}")
            return
        
        print("\n✅ Tool-by-tool test completed!")
        
    except Exception as e:
        print(f"❌ Tool-by-tool test failed: {e}")
        import traceback
        traceback.print_exc()


def run_interactive():
    """
    Run interactive mode for the AI Chef Assistant.
    """
    print("🧑‍🍳 AI Chef Assistant - Interactive Mode")
    print("=" * 50)
    print("Type 'help' for available commands, 'quit' to exit")
    print()
    
    try:
        agent = create_chef_agent()
        
        while True:
            try:
                user_input = input("👨‍🍳 Chef> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    show_help()
                    continue
                elif user_input.lower() == 'test':
                    run_test()
                    continue
                elif not user_input:
                    continue
                
                # Run the user's query
                print(f"🤖 Processing: {user_input}")
                result = agent.run(user_input)
                print(f"📋 Result: {result}")
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Failed to start interactive mode: {e}")


def run_natural_language_request_with_queue(user_prompt, dietary_restrictions=None):
    """
    Run a natural language request using a queue-based approach for better reliability.
    
    Args:
        user_prompt (str): The user's natural language request
        dietary_restrictions (list): List of dietary restrictions (e.g., ['vegan', 'keto'])
    """
    print("🧑‍🍳 AI Chef Assistant - Natural Language Request (Queue-Based)")
    print("=" * 60)
    
    if dietary_restrictions:
        print(f"🥗 Dietary restrictions: {', '.join(dietary_restrictions)}")
    
    print(f"🎯 User request: {user_prompt}")
    print("=" * 60)
    
    try:
        # Step 1: Search for recipes once
        print("🔍 Step 1: Searching for recipes...")
        from tools.recipe_search import RecipeSearchTool
        search_tool = RecipeSearchTool()
        
        # Extract the main food item from the user prompt
        # Simple extraction - look for common food words
        food_keywords = ['cookies', 'pancakes', 'bread', 'cake', 'pasta', 'soup', 'salad', 'pizza', 'chicken', 'beef', 'fish', 'rice', 'quinoa', 'smoothie', 'muffins', 'brownies', 'pie', 'tart', 'sauce', 'dressing']
        
        search_query = "cookies"  # default
        for keyword in food_keywords:
            if keyword in user_prompt.lower():
                search_query = keyword
                break
        
        if dietary_restrictions:
            search_result = search_tool.forward(search_query, dietary_restrictions)
        else:
            search_result = search_tool.forward(search_query)
        
        import json
        search_data = json.loads(search_result)
        
        print(f"🔍 Search result: {search_result[:200]}...")
        print(f"🔍 Search success: {search_data.get('success')}")
        print(f"🔍 Number of recipes: {len(search_data.get('recipes', []))}")
        
        if not search_data.get('success') or not search_data.get('recipes'):
            print("❌ No recipes found in search")
            return
        
        # Step 2: Create queue of recipe URLs
        recipe_queue = []
        for recipe in search_data['recipes']:
            recipe_queue.append({
                'title': recipe.get('title', 'Unknown'),
                'url': recipe.get('url', ''),
                'description': recipe.get('description', '')
            })
        
        print(f"📋 Found {len(recipe_queue)} recipes to try:")
        for i, recipe in enumerate(recipe_queue):
            print(f"  {i+1}. {recipe['title']}")
        
        # Step 3: Process recipes one by one using the agent for extraction
        agent = create_chef_agent()
        
        for i, recipe in enumerate(recipe_queue):
            print(f"\n🔍 Step {i+2}: Trying recipe {i+1}/{len(recipe_queue)}")
            print(f"   Title: {recipe['title']}")
            print(f"   URL: {recipe['url']}")
            
            # Use the agent to extract and format the recipe
            extraction_prompt = f"""Extract recipe from this URL: {recipe['url']}

IMPORTANT: The recipe_extraction_llm tool returns a JSON STRING, not a dictionary.

Follow these steps exactly:
1. Call recipe_extraction_llm(url='{recipe['url']}') and store the result in a variable
2. Parse the JSON string using: import json; data = json.loads(result)
3. Check if data['success'] is True and data['recipe']['ingredients'] and data['recipe']['instructions'] exist
4. If successful, call final_answer(data) with the complete data
5. If not successful, do not call final_answer()

Example:
result = recipe_extraction_llm(url='{recipe['url']}')
data = json.loads(result)
if data['success'] and data['recipe']['ingredients'] and data['recipe']['instructions']:
    final_answer(data)"""
            
            try:
                result = agent.run(extraction_prompt)
                
                # Debug: Print what the agent actually returned
                print(f"🔍 Agent returned: {type(result)} - {str(result)[:200]}...")
                
                # Check if the agent successfully extracted a recipe
                success = False
                recipe_data = {}
                ingredients = []
                instructions = []
                
                # Handle different response formats from the agent
                if isinstance(result, dict):
                    # Format 1: Agent returns dict directly with recipe data
                    print(f"🔍 Agent returned dict format")
                    if 'recipe' in result:
                        recipe_data = result['recipe']
                        ingredients = recipe_data.get('ingredients', [])
                        instructions = recipe_data.get('instructions', [])
                        if ingredients and instructions:
                            success = True
                            print(f"✅ Successfully parsed dict recipe with {len(ingredients)} ingredients and {len(instructions)} steps")
                else:
                    # Format 2: Agent returns AgentText with JSON string
                    print(f"🔍 Agent returned AgentText format")
                    result_str = str(result)
                    
                    # Check if the result contains a successful extraction
                    if '{"success": true' in result_str and '"ingredients":' in result_str and '"instructions":' in result_str:
                        print(f"🔍 Found successful extraction in agent response")
                        
                        # Try to extract the JSON from the response
                        try:
                            import json
                            import re
                            
                            # Find the JSON part of the response
                            json_match = re.search(r'\{.*"success":\s*true.*\}', result_str, re.DOTALL)
                            if json_match:
                                json_str = json_match.group(0)
                                result_data = json.loads(json_str)
                                recipe_data = result_data.get('recipe', {})
                                ingredients = recipe_data.get('ingredients', [])
                                instructions = recipe_data.get('instructions', [])
                                
                                # Check if we have meaningful content
                                if ingredients and instructions:
                                    success = True
                                    print(f"✅ Successfully parsed JSON recipe with {len(ingredients)} ingredients and {len(instructions)} steps")
                        except Exception as e:
                            print(f"❌ Failed to parse JSON from agent response: {e}")
                
                # Check if we got a successful result
                if success:
                    print(f"✅ Success! Found recipe with {len(ingredients)} ingredients and {len(instructions)} steps")
                    
                    # Format the final result
                    final_result = {
                        'title': recipe_data.get('title', recipe['title']),
                        'ingredients': [ing.get('ingredient', ing.get('raw_text', str(ing))) for ing in ingredients],
                        'instructions': [inst.get('instruction', inst.get('step', str(inst))) for inst in instructions],
                        'prep_time': recipe_data.get('prep_time', ''),
                        'cook_time': recipe_data.get('cook_time', ''),
                        'servings': recipe_data.get('servings', ''),
                        'url': recipe['url']
                    }
                    
                    print("\n📋 Final Recipe:")
                    print("=" * 20)
                    print(f"Title: {final_result['title']}")
                    print(f"Ingredients ({len(final_result['ingredients'])}):")
                    for ing in final_result['ingredients']:
                        print(f"  - {ing}")
                    print(f"Instructions ({len(final_result['instructions'])}):")
                    for j, inst in enumerate(final_result['instructions'], 1):
                        print(f"  {j}. {inst}")
                    
                    # Step 4: Scale the recipe if the user prompt indicates a specific serving size
                    print(f"\n🔍 Step {i+3}: Checking for scaling requirements...")
                    scaling_result = scale_recipe_if_needed(final_result, user_prompt, agent)
                    if scaling_result:
                        return scaling_result
                    
                    return final_result
                else:
                    print(f"❌ Recipe {i+1} failed: Agent extraction unsuccessful")
                    
            except Exception as e:
                print(f"❌ Recipe {i+1} failed: {e}")
        
        print("\n❌ All recipes failed to extract properly")
        return None
        
    except Exception as e:
        print(f"❌ Queue-based request failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_natural_language_request(user_prompt, dietary_restrictions=None):
    """
    Run a natural language request through the full agent pipeline.
    
    Args:
        user_prompt (str): The user's natural language request
        dietary_restrictions (list): List of dietary restrictions (e.g., ['vegan', 'keto'])
    """
    print("🧑‍🍳 AI Chef Assistant - Natural Language Request")
    print("=" * 50)
    
    if dietary_restrictions:
        print(f"🥗 Dietary restrictions: {', '.join(dietary_restrictions)}")
    
    print(f"🎯 User request: {user_prompt}")
    print("=" * 50)
    
    try:
        agent = create_chef_agent()
        
        # Create a simple, direct prompt for the agent
        if dietary_restrictions:
            restrictions_str = ', '.join(dietary_restrictions)
            full_prompt = f"Find a {restrictions_str} recipe for {user_prompt}. Use recipe_search tool, then recipe_extraction tool. Parse the JSON response with json.loads(). If the extraction has 'success': true and non-empty ingredients/instructions, call final_answer() with the recipe data. Do not search again."
        else:
            full_prompt = f"Find a recipe for {user_prompt}. Use recipe_search tool, then recipe_extraction tool. Parse the JSON response with json.loads(). If the extraction has 'success': true and non-empty ingredients/instructions, call final_answer() with the recipe data. Do not search again."
        
        print(f"🤖 Processing: {full_prompt}")
        print("=" * 50)
        
        # Run the agent with the natural language prompt
        result = agent.run(full_prompt)
        
        print("📋 Recipe Results:")
        print("=" * 20)
        print(result)
        
        # Parse the result to validate it contains the expected elements
        print("\n🔍 Validation:")
        print("=" * 15)
        
        # Check if we got a structured recipe response
        if isinstance(result, dict) and 'title' in result and 'ingredients' in result and 'instructions' in result:
            print("✅ Recipe search successful")
            print("✅ Recipe extraction successful")
            print(f"✅ Recipe contains {len(result['ingredients'])} ingredients and {len(result['instructions'])} steps")
            print(f"✅ Recipe title: {result['title']}")
        elif "RECIPE_FOUND:" in str(result):
            print("✅ Recipe search successful (legacy format)")
        else:
            print("❌ Recipe search failed")
            
        if "RECIPE_EXTRACTED:" in str(result):
            print("✅ Recipe extraction successful (legacy format)")
        elif isinstance(result, dict) and 'ingredients' in result and 'instructions' in result:
            print("✅ Recipe extraction successful (structured format)")
        else:
            print("❌ Recipe extraction failed")
            
        if "INGREDIENTS:" in str(result) and "STEPS:" in str(result):
            print("✅ Recipe contains ingredients and steps (legacy format)")
        elif isinstance(result, dict) and 'ingredients' in result and 'instructions' in result:
            print("✅ Recipe contains ingredients and steps (structured format)")
        else:
            print("❌ Recipe missing ingredients or steps")
        
        print("\n✅ Natural language request completed!")
        
    except Exception as e:
        print(f"❌ Natural language request failed: {e}")
        import traceback
        traceback.print_exc()


def scale_recipe_if_needed(recipe_data, user_prompt, agent):
    """
    Check if the user prompt indicates a need for scaling and scale the recipe if needed.
    
    Args:
        recipe_data (dict): The extracted recipe data
        user_prompt (str): The original user prompt
        agent: The agent instance
        
    Returns:
        dict: Scaled recipe data if scaling was needed, None otherwise
    """
    # Check if the user prompt indicates a specific serving size
    serving_indicators = [
        'for', 'people', 'guests', 'servings', 'family', 'party', 'gathering',
        'dinner party', 'large family', 'small', 'couple', 'just me'
    ]
    
    prompt_lower = user_prompt.lower()
    needs_scaling = any(indicator in prompt_lower for indicator in serving_indicators)
    
    if not needs_scaling:
        print("   No scaling needed - user prompt doesn't indicate specific serving size")
        return None
    
    print("   User prompt indicates scaling needed - scaling recipe...")
    
    try:
        # Convert recipe data to JSON string for the scaling tool
        recipe_json = json.dumps({
            "success": True,
            "recipe": recipe_data
        })
        
        # Use the agent to scale the recipe
        scaling_prompt = f"""Scale this recipe based on the user's request: "{user_prompt}"

Recipe data: {recipe_json}

IMPORTANT: The recipe_scaling_llm tool expects a JSON STRING, not a dictionary.

Follow these steps exactly:
1. Call recipe_scaling_llm(recipe_data=recipe_json, target_servings='auto', user_prompt='{user_prompt}')
2. The result is a JSON STRING - you need to parse it with json.loads()
3. Parse the result: import json; result_data = json.loads(scaled_result)
4. Check if result_data['success'] is True and return the scaled recipe data
5. If scaling is successful, call final_answer(result_data) with the complete scaling result

You MUST call final_answer() with the scaled recipe data or error message. Do not stop until you call final_answer()."""
        
        result = agent.run(scaling_prompt)
        
        # Parse the scaling result
        if isinstance(result, dict) and result.get('success'):
            print("   ✅ Recipe scaled successfully!")
            return result
        else:
            print("   ❌ Recipe scaling failed")
            return None
            
    except Exception as e:
        print(f"   ❌ Recipe scaling failed: {e}")
        return None


def run_scaling(recipe_json, target_servings, user_prompt=None):
    """
    Run recipe scaling to target serving size.
    
    Args:
        recipe_json (str): JSON string containing recipe data
        target_servings (str): Target number of servings
        user_prompt (str): Original user prompt for serving size detection
    """
    try:
        # Create agent
        agent = create_chef_agent()
        
        # Build the scaling prompt
        scaling_prompt = f"""Scale this recipe to {target_servings} servings:

Recipe data: {recipe_json}

IMPORTANT: The recipe_scaling tool expects a JSON STRING, not a dictionary.

Follow these steps exactly:
1. Convert the recipe data to a JSON string using: import json; recipe_json_string = json.dumps(recipe_data)
2. Call recipe_scaling(recipe_data=recipe_json_string, target_servings='{target_servings}')
3. The result is already a dictionary - no need to parse with json.loads()
4. Check if result['success'] is True and return the scaled recipe data

You MUST call final_answer() with the scaled recipe data or error message. Do not stop until you call final_answer()."""
        
        result = agent.run(scaling_prompt)
        
        print("📋 Scaling Result:")
        print("=" * 20)
        print(result)
        
    except Exception as e:
        print(f"❌ Scaling failed: {e}")


def main():
    """
    Main function with command-line argument handling.
    """
    if len(sys.argv) == 1:
        # No arguments - run interactive mode
        run_interactive()
    elif len(sys.argv) == 2:
        command = sys.argv[1].lower()
        if command == 'help':
            show_help()
        elif command == 'test':
            run_test()
        elif command == 'e2e':
            run_natural_language_request_with_queue("I'd like some pancakes please")  # No dietary restrictions for basic e2e test
        elif command == 'tools':
            run_end_to_end_test_with_tool_outputs(['vegan'])  # Default to vegan for tools test
        else:
            # Treat as natural language request without restrictions
            run_natural_language_request_with_queue(sys.argv[1])
    elif len(sys.argv) == 3:
        # Check if this is a natural language request (quoted string) or legacy command
        first_arg = sys.argv[1]
        second_arg = sys.argv[2].lower()
        
        # If second arg is a known command, treat as legacy format
        if second_arg in ['search', 'extract']:
            if second_arg == 'search':
                run_search(first_arg)
            elif second_arg == 'extract':
                run_extraction(first_arg)
        else:
            # Treat as natural language request without restrictions
            run_natural_language_request(first_arg)
    elif len(sys.argv) == 4:
        # Check if this is a natural language request with restrictions
        user_prompt = sys.argv[1]
        flag = sys.argv[2]
        restrictions_str = sys.argv[3]
        
        if flag == '--restrictions':
            # Parse dietary restrictions (comma-separated)
            restrictions_list = [r.strip().lower() for r in restrictions_str.split(',')]
            run_natural_language_request_with_queue(user_prompt, restrictions_list)
        else:
            # Legacy command format
            command = sys.argv[1].lower()
            diet_flag = sys.argv[2]
            diet_restrictions = sys.argv[3]
            
            if command == 'e2e' and diet_flag == '--diet':
                # Parse dietary restrictions (comma-separated)
                restrictions_list = [r.strip().lower() for r in diet_restrictions.split(',')]
                run_natural_language_request_with_queue("I'd like some pancakes please", restrictions_list)
            else:
                print(f"❌ Unknown command or flag: {command} {diet_flag}")
                print("Use 'python3.11 chef_agent.py help' for usage information")
    elif len(sys.argv) == 5:
        command = sys.argv[1].lower()
        query = sys.argv[2]
        diet_flag = sys.argv[3]
        diet_restrictions = sys.argv[4]
        
        if command == 'search' and diet_flag == '--diet':
            # Parse dietary restrictions (comma-separated)
            restrictions_list = [r.strip().lower() for r in diet_restrictions.split(',')]
            run_search(query, restrictions_list)
        elif command == 'e2e' and diet_flag == '--diet':
            # Parse dietary restrictions (comma-separated)
            restrictions_list = [r.strip().lower() for r in diet_restrictions.split(',')]
            run_natural_language_request_with_queue("I'd like some pancakes please", restrictions_list)
        elif command == 'tools' and diet_flag == '--diet':
            # Parse dietary restrictions (comma-separated)
            restrictions_list = [r.strip().lower() for r in diet_restrictions.split(',')]
            run_end_to_end_test_with_tool_outputs(restrictions_list)
        else:
            print(f"❌ Unknown command or flag: {command} {diet_flag}")
            print("Use 'python3.11 chef_agent.py help' for usage information")
    else:
        print("❌ Invalid number of arguments")
        print("Use 'python3.11 chef_agent.py help' for usage information")


if __name__ == "__main__":
    main()
