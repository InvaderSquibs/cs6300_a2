#!/usr/bin/env python3.11
"""
AI Chef Assistant Agent

A multi-tooled agent that helps with recipe curation and modification.
Uses smolagents framework with specialized tools for recipe management.
"""

from smolagents import CodeAgent, Tool
from smolagents import OpenAIServerModel
import dotenv
import os

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
        additional_authorized_imports=[],
        max_steps=5  # Allow more steps for complex recipe tasks
    )
    
    return agent


def main():
    """
    Main function to test the AI Chef Assistant.
    """
    print("🧑‍🍳 AI Chef Assistant - Testing Tool Connection")
    print("=" * 50)
    
    try:
        # Create the agent
        agent = create_chef_agent()
        
        # Test the recipe search tool
        print("Testing recipe search tool...")
        answer = agent.run("Say hello to Squibs using the recipe_search tool")
        print(f"Agent response: {answer}")
        
        print("\n✅ Tool connection test successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
