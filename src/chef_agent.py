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
    
    # TODO: Add more tools as we build them
    # recipe_scaling_tool = RecipeScalingTool()
    # recipe_validation_tool = RecipeValidationTool()
    
    tools = [recipe_search_tool]
    
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
    print("  python3.11 chef_agent.py test               # Test connection")
    print()
    print("AVAILABLE TOOLS:")
    print("=" * 20)
    
    # Show tool information
    try:
        # Create tools directly instead of through agent
        recipe_search_tool = RecipeSearchTool()
        tools = [recipe_search_tool]
        
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
        
        search_prompt += ". The tool returns a JSON string - use json.loads() to parse it, then extract the recipe title, URL, and description from the 'recipes' array. You MUST call final_answer() with the format: 'RECIPE_FOUND: [title] | URL: [url] | DESCRIPTION: [description]' or 'NO_RECIPES_FOUND: [error message]'. Do not stop until you call final_answer(). Use the exact query '{query}' - do not substitute it with something else."
        
        result = agent.run(search_prompt)
        
        print("📋 Search Results:")
        print(result)
            
    except Exception as e:
        print(f"❌ Search failed: {e}")
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
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python3.11 chef_agent.py help' for usage information")
    elif len(sys.argv) == 3:
        command = sys.argv[1].lower()
        query = sys.argv[2]
        if command == 'search':
            run_search(query)
        else:
            print(f"❌ Unknown command: {command}")
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
        else:
            print(f"❌ Unknown command or flag: {command} {diet_flag}")
            print("Use 'python3.11 chef_agent.py help' for usage information")
    else:
        print("❌ Invalid number of arguments")
        print("Use 'python3.11 chef_agent.py help' for usage information")


if __name__ == "__main__":
    main()
