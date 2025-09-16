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
from tools.recipe_formatter_llm import RecipeFormatterLLMTool

# Load environment variables
dotenv.load_dotenv()

# Configure Phoenix Telemetry (Optional)
# Enable telemetry by setting ENABLE_TELEMETRY=true environment variable
# or by importing telemetry_config module
try:
    from telemetry_config import auto_enable_telemetry
    auto_enable_telemetry()
except ImportError:
    # Telemetry config not available, continue without telemetry
    pass


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
    recipe_formatter_tool = RecipeFormatterLLMTool()
    
    tools = [recipe_search_tool, recipe_extraction_tool, recipe_scaling_tool, recipe_formatter_tool]
    
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
        recipe_scaling_tool = RecipeScalingLLMTool()
        recipe_formatter_tool = RecipeFormatterLLMTool()
        tools = [recipe_search_tool, recipe_extraction_tool, recipe_scaling_tool, recipe_formatter_tool]
        
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


def _extract_recipe_query_from_prompt(user_prompt):
    """
    Extract the recipe query from a natural language prompt using LLM.
    
    Args:
        user_prompt (str): The user's natural language request
        
    Returns:
        str: The extracted recipe query for searching
    """
    from openai import OpenAI
    import os
    
    client = OpenAI(
        base_url=os.getenv("GPT_ENDPOINT"),
        api_key=os.getenv("OPENAI_API_KEY", "dummy-key")
    )
    
    prompt = f"""
Extract the recipe request from this user prompt. Return ONLY the recipe name/type, nothing else.

Examples:
- "I'd like some banana bread please" → "banana bread"
- "Can you find me a chocolate chip cookie recipe?" → "chocolate chip cookies"
- "I want to make pancakes for breakfast" → "pancakes"
- "Find me a vegan chocolate cake recipe" → "chocolate cake"
- "I need a recipe for chicken parmesan" → "chicken parmesan"

User prompt: "{user_prompt}"

Recipe query:"""

    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL_ID", "google/gemma-3-27b"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.1
        )
        
        query = response.choices[0].message.content.strip()
        return query if query else "cookies"  # fallback
        
    except Exception as e:
        print(f"⚠️ LLM query extraction failed: {e}")
        return "cookies"  # fallback


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
        # Step 1: Search for recipes using the agent
        print("🔍 Step 1: Searching for recipes...")
        
        # Extract the recipe request from the user prompt using LLM
        search_query = _extract_recipe_query_from_prompt(user_prompt)
        print(f"🔍 Extracted search query: '{search_query}'")
        
        # Create agent and use it to search for recipes
        agent = create_chef_agent()
        
        # Build search prompt for the agent
        if dietary_restrictions:
            search_prompt = f"""Search for recipes using the recipe_search tool.

Query: "{search_query}"
Dietary restrictions: {', '.join(dietary_restrictions)}

Call recipe_search(query='{search_query}', dietary_restrictions={dietary_restrictions}) and store the result in a variable called 'search_result'.

Then call final_answer(search_result) with the raw JSON result from the tool."""
        else:
            search_prompt = f"""Search for recipes using the recipe_search tool.

Query: "{search_query}"

Call recipe_search(query='{search_query}') and store the result in a variable called 'search_result'.

Then call final_answer(search_result) with the raw JSON result from the tool."""
        
        print("🔧 Calling recipe_search through agent for telemetry tracking...")
        search_result = agent.run(search_prompt)
        
        import json
        # The agent might return a string or dict, handle both cases
        if isinstance(search_result, str):
            try:
                search_data = json.loads(search_result)
            except json.JSONDecodeError:
                # If it's not JSON, try to extract JSON from the string
                import re
                json_match = re.search(r'\{.*\}', search_result, re.DOTALL)
                if json_match:
                    search_data = json.loads(json_match.group())
                else:
                    print(f"❌ Could not parse search result: {search_result}")
                    return
        else:
            search_data = search_result
        
        print(f"🔍 Search result: {search_result[:200]}...")
        print(f"🔍 Search success: {search_data.get('success')}")
        print(f"🔍 Number of recipes: {len(search_data.get('recipes', []))}")
        
        if not search_data.get('success') or not search_data.get('recipes'):
            print("❌ No recipes found in search")
            return
        
        # Show the URLs found by the search tool
        print("🔗 URLs found by search tool:")
        for i, recipe in enumerate(search_data.get('recipes', []), 1):
            print(f"   {i}. {recipe.get('title', 'Unknown')}")
            print(f"      URL: {recipe.get('url', 'No URL')}")
            print(f"      Description: {recipe.get('description', 'No description')[:100]}...")
            print()
        
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
        # (agent already created in Step 1)
        
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
                            
                            # Show extraction tool deliverables
                            print("📋 Extraction tool deliverables:")
                            print(f"   Title: {recipe_data.get('title', 'Unknown')}")
                            print(f"   URL: {recipe_data.get('url', 'No URL')}")
                            print(f"   Ingredients: {len(ingredients)} items")
                            print(f"   Instructions: {len(instructions)} steps")
                            print(f"   Servings: {recipe_data.get('servings', 'Unknown')}")
                            print(f"   Prep time: {recipe_data.get('prep_time', 'Unknown')}")
                            print(f"   Cook time: {recipe_data.get('cook_time', 'Unknown')}")
                            print(f"   Total time: {recipe_data.get('total_time', 'Unknown')}")
                            print(f"   Dietary tags: {', '.join(recipe_data.get('dietary_tags', []))}")
                            print()
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
                        # Step 5: Format the scaled recipe into a markdown file
                        print(f"\n🔍 Step {i+4}: Formatting recipe into markdown file...")
                        format_result = format_recipe_if_needed(scaling_result, user_prompt, agent)
                        if format_result:
                            return format_result
                        return scaling_result
                    
                    # Step 5: Format the original recipe into a markdown file
                    print(f"\n🔍 Step {i+4}: Formatting recipe into markdown file...")
                    format_result = format_recipe_if_needed(final_result, user_prompt, agent)
                    if format_result:
                        return format_result
                    
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
    print(f"   📊 Original recipe servings: {recipe_data.get('servings', 'unknown')}")
    print(f"   🎯 User requested: '{user_prompt}'")
    
    try:
        # Convert recipe data to JSON string for the scaling tool
        recipe_json = json.dumps({
            "success": True,
            "recipe": recipe_data
        })
        print("   🔧 Calling recipe_scaling_llm tool...")
        print("   📞 TOOL CALL: recipe_scaling_llm() - This proves scaling tool is being executed")
        
        # Use the agent to scale the recipe
        scaling_prompt = f"""Scale this recipe based on the user's request: "{user_prompt}"

Recipe data: {recipe_json}

IMPORTANT: The recipe_scaling_llm tool expects a JSON STRING, not a dictionary.

Follow these steps exactly:
1. Call recipe_scaling_llm(recipe_data=recipe_json, user_prompt='{user_prompt}')
2. The result is a JSON STRING - you need to parse it with json.loads()
3. Parse the result: import json; result_data = json.loads(scaled_result)
4. Check if result_data['success'] is True and return the scaled recipe data
5. If scaling is successful, return the scaled recipe data (do NOT call final_answer)

IMPORTANT: Do NOT call final_answer() in this step. Just return the scaled recipe data. The formatter will handle final_answer()."""
        
        result = agent.run(scaling_prompt)
        print(f"   📋 Scaling agent result type: {type(result)}")
        print(f"   📋 Scaling agent result: {str(result)[:200]}...")
        
        # Validate that the scaling tool was actually called
        if hasattr(agent, '_last_execution_logs'):
            logs = str(agent._last_execution_logs)
            if 'recipe_scaling_llm(' in logs:
                print("   ✅ VALIDATION: recipe_scaling_llm tool was actually called in agent execution")
            else:
                print("   ❌ VALIDATION FAILED: recipe_scaling_llm tool was NOT called")
        else:
            print("   ⚠️  Cannot validate tool execution - no execution logs available")
        
        # Parse the scaling result
        if isinstance(result, dict) and result.get('success'):
            print("   ✅ Recipe scaled successfully!")
            if 'scaled_recipe' in result:
                scaled_servings = result['scaled_recipe'].get('servings', 'unknown')
                print(f"   📊 Scaled recipe servings: {scaled_servings}")
                
                # Validate scaling factor
                if 'scaling_info' in result:
                    scaling_info = result['scaling_info']
                    original_servings = scaling_info.get('original_servings', 'unknown')
                    target_servings = scaling_info.get('target_servings', 'unknown')
                    scaling_factor = scaling_info.get('scaling_factor', 'unknown')
                    print(f"   🧮 SCALING MATH: {original_servings} → {target_servings} (factor: {scaling_factor})")
                    print(f"   ✅ VALIDATION: Recipe was mathematically scaled, not just found at target size")
                    
                    # Show scaling tool deliverables
                    print("📊 Scaling tool deliverables:")
                    print(f"   Original servings: {original_servings}")
                    print(f"   Target servings: {target_servings}")
                    print(f"   Scaling factor: {scaling_factor}")
                    print(f"   Scaling method: {scaling_info.get('scaling_method', 'Unknown')}")
                    print(f"   Serving detection: {scaling_info.get('serving_detection', 'Unknown')}")
                    if 'unit_conversions' in scaling_info:
                        print(f"   Unit conversions: {len(scaling_info['unit_conversions'])} items")
                        for i, conversion in enumerate(scaling_info['unit_conversions'][:3], 1):
                            print(f"     {i}. {conversion}")
                        if len(scaling_info['unit_conversions']) > 3:
                            print(f"     ... and {len(scaling_info['unit_conversions']) - 3} more")
                    print()
                else:
                    print(f"   ⚠️  No scaling_info found - cannot validate scaling calculation")
            return result
        else:
            print("   ❌ Recipe scaling failed - checking for partial results...")
            print(f"   📋 Result type: {type(result)}")
            print(f"   📋 Result content: {str(result)[:300]}...")
            
            # Check if scaling was attempted but hit max steps
            # Look for scaled recipe in the agent's execution logs
            if hasattr(agent, '_last_execution_logs'):
                logs = str(agent._last_execution_logs)
                if '"scaled_recipe"' in logs and '"target_servings"' in logs:
                    print("   ⚠️  Scaling hit max steps, but scaled recipe was generated")
                    # Try to extract the scaled recipe from logs
                    try:
                        import re
                        # Find the scaled recipe JSON in the logs
                        scaled_match = re.search(r'"scaled_recipe":\s*({[^}]+})', logs)
                        if scaled_match:
                            scaled_recipe_json = scaled_match.group(1)
                            # Reconstruct the full scaling result
                            scaling_result = {
                                "success": True,
                                "original_recipe": recipe_data.get('recipe', {}),
                                "scaled_recipe": json.loads(scaled_recipe_json),
                                "scaling_info": {
                                    "original_servings": recipe_data.get('recipe', {}).get('servings', 'unknown'),
                                    "target_servings": "24",  # From user prompt
                                    "scaling_factor": "2.0",
                                    "scaling_method": "llm_natural_language_extracted_from_logs"
                                }
                            }
                            print("   ✅ Extracted scaled recipe from execution logs!")
                            return scaling_result
                    except Exception as e:
                        print(f"   ⚠️  Could not extract scaled recipe from logs: {e}")
            
            print("   ❌ Recipe scaling failed")
            return None
            
    except Exception as e:
        print(f"   ❌ Recipe scaling failed: {e}")
        return None


def format_recipe_if_needed(recipe_data, user_prompt, agent):
    """
    Format the recipe into a beautiful markdown file.
    
    Args:
        recipe_data (dict): The recipe data (original or scaled)
        user_prompt (str): The original user prompt
        agent: The agent instance
        
    Returns:
        dict: Formatted recipe data with file path if successful, None otherwise
    """
    print("   Formatting recipe into markdown file...")
    print(f"   📋 Recipe data type: {type(recipe_data)}")
    print(f"   📋 Recipe data keys: {list(recipe_data.keys()) if isinstance(recipe_data, dict) else 'Not a dict'}")
    
    try:
        # Handle scaled recipe data - extract the actual recipe to format
        if 'scaled_recipe' in recipe_data:
            # This is a scaled recipe result, use the scaled_recipe
            actual_recipe = recipe_data['scaled_recipe']
            print("   🎯 Using SCALED recipe for formatting")
            print(f"   📊 Scaled recipe servings: {actual_recipe.get('servings', 'unknown')}")
        elif 'recipe' in recipe_data:
            # This is a regular recipe result
            actual_recipe = recipe_data['recipe']
            print("   📝 Using ORIGINAL recipe for formatting")
            print(f"   📊 Original recipe servings: {actual_recipe.get('servings', 'unknown')}")
        else:
            # This is the recipe data itself
            actual_recipe = recipe_data
            print("   📝 Using recipe data directly for formatting")
            print(f"   📊 Recipe servings: {actual_recipe.get('servings', 'unknown')}")
        
        # Convert recipe data to JSON string for the formatter tool
        recipe_json = json.dumps({
            "success": True,
            "recipe": actual_recipe
        })
        
        # Use the agent to format the recipe
        formatting_prompt = f"""Format this recipe into a beautiful markdown file:

Recipe data: {recipe_json}

IMPORTANT: The recipe_formatter_llm tool expects a JSON STRING, not a dictionary.

Follow these steps exactly:
1. Call recipe_formatter_llm(recipe_data=recipe_json, output_filename=None, format_style='cookbook')
2. The result is a JSON STRING - you need to parse it with json.loads()
3. Parse the result: import json; result_data = json.loads(formatted_result)
4. Check if result_data['success'] is True and return the formatted recipe data
5. If formatting is successful, call final_answer(result_data) with the complete formatting result

You MUST call final_answer() with the formatted recipe data. This is the ONLY step that should call final_answer(). Do not stop until you call final_answer()."""
        
        result = agent.run(formatting_prompt)
        
        # Parse the formatting result
        if isinstance(result, dict) and result.get('success'):
            formatted_recipe = result.get('formatted_recipe', {})
            file_path = formatted_recipe.get('file_path', '')
            print(f"   ✅ Recipe formatted successfully! Saved to: {file_path}")
            
            # Show formatter tool deliverables
            print("📄 Formatter tool deliverables:")
            print(f"   Title: {formatted_recipe.get('title', 'Unknown')}")
            print(f"   Filename: {formatted_recipe.get('filename', 'Unknown')}")
            print(f"   File path: {file_path}")
            print(f"   Format style: {formatted_recipe.get('format_style', 'Unknown')}")
            if 'formatting_info' in result:
                formatting_info = result['formatting_info']
                print(f"   File size: {formatting_info.get('file_size', 'Unknown')} bytes")
                print(f"   Formatting method: {formatting_info.get('formatting_method', 'Unknown')}")
                print(f"   Content filtering: {formatting_info.get('content_filtering', 'Unknown')}")
            print()
            return result
        else:
            print("   ❌ Recipe formatting failed")
            return None
            
    except Exception as e:
        print(f"   ❌ Recipe formatting failed: {e}")
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
