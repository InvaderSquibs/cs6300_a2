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
from tools.recipe_extraction import RecipeExtractionTool

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
    recipe_extraction_tool = RecipeExtractionTool()
    
    # TODO: Add more tools as we build them
    # recipe_scaling_tool = RecipeScalingTool()
    # recipe_validation_tool = RecipeValidationTool()
    
    tools = [recipe_search_tool, recipe_extraction_tool]
    
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
        max_steps=5  # Allow more steps for complex recipe tasks
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
    print("  python3.11 chef_agent.py search \"query\"     # Search for recipes")
    print("  python3.11 chef_agent.py search \"query\" --diet \"restrictions\"  # Search with dietary restrictions")
    print("  python3.11 chef_agent.py extract \"url\"      # Extract recipe from URL")
    print("  python3.11 chef_agent.py test               # Test connection")
    print("  python3.11 chef_agent.py e2e                # End-to-end test (vegan pancakes)")
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
        recipe_extraction_tool = RecipeExtractionTool()
        tools = [recipe_search_tool, recipe_extraction_tool]
        
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
    print('  python3.11 chef_agent.py search "pancakes"')
    print('  python3.11 chef_agent.py search "pancakes" --diet "vegan,gluten-free"')
    print('  python3.11 chef_agent.py search "bread" --diet "keto"')
    print('  python3.11 chef_agent.py search "cookies" --diet "paleo,dairy-free"')
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
        
        from tools.recipe_extraction import RecipeExtractionTool
        extraction_tool = RecipeExtractionTool()
        
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
            run_end_to_end_test()  # No dietary restrictions for basic e2e test
        elif command == 'tools':
            run_end_to_end_test_with_tool_outputs(['vegan'])  # Default to vegan for tools test
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python3.11 chef_agent.py help' for usage information")
    elif len(sys.argv) == 3:
        command = sys.argv[1].lower()
        query = sys.argv[2]
        if command == 'search':
            run_search(query)
        elif command == 'extract':
            run_extraction(query)
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python3.11 chef_agent.py help' for usage information")
    elif len(sys.argv) == 4:
        command = sys.argv[1].lower()
        diet_flag = sys.argv[2]
        diet_restrictions = sys.argv[3]
        
        if command == 'e2e' and diet_flag == '--diet':
            # Parse dietary restrictions (comma-separated)
            restrictions_list = [r.strip().lower() for r in diet_restrictions.split(',')]
            run_end_to_end_test(restrictions_list)
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
            run_end_to_end_test(restrictions_list)
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
