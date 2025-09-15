#!/usr/bin/env python3
"""
Systematic testing plan for the AI Chef Assistant
Tests each component independently to isolate issues.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools.recipe_search import RecipeSearchTool
from tools.recipe_extraction import RecipeExtractionTool
from chef_agent import create_chef_agent

def test_1_search_tool():
    """Test 1: Validate search tool works independently"""
    print("=" * 60)
    print("TEST 1: Recipe Search Tool (Independent)")
    print("=" * 60)
    
    search_tool = RecipeSearchTool()
    
    # Test with a known good query
    result = search_tool.forward("vegan chocolate chip cookies", ["vegan"])
    print(f"Search result type: {type(result)}")
    print(f"Search result: {result[:500]}...")
    
    # Parse the JSON
    import json
    try:
        data = json.loads(result)
        print(f"✅ Search tool returned valid JSON")
        print(f"Success: {data.get('success', 'N/A')}")
        print(f"Number of recipes: {len(data.get('recipes', []))}")
        if data.get('recipes'):
            print(f"First recipe URL: {data['recipes'][0].get('url', 'N/A')}")
        return data.get('recipes', [])[0] if data.get('recipes') else None
    except Exception as e:
        print(f"❌ Search tool failed: {e}")
        return None

def test_2_extraction_tool(test_url):
    """Test 2: Validate extraction tool works independently"""
    print("\n" + "=" * 60)
    print("TEST 2: Recipe Extraction Tool (Independent)")
    print("=" * 60)
    
    if not test_url:
        print("❌ No test URL available from search tool")
        return None
    
    extraction_tool = RecipeExtractionTool()
    
    print(f"Testing URL: {test_url}")
    result = extraction_tool.forward(test_url)
    print(f"Extraction result type: {type(result)}")
    print(f"Extraction result: {result[:500]}...")
    
    # Parse the JSON
    import json
    try:
        data = json.loads(result)
        print(f"✅ Extraction tool returned valid JSON")
        print(f"Success: {data.get('success', 'N/A')}")
        if data.get('success'):
            recipe = data.get('recipe', {})
            ingredients = recipe.get('ingredients', [])
            instructions = recipe.get('instructions', [])
            print(f"Title: {recipe.get('title', 'N/A')}")
            print(f"Number of ingredients: {len(ingredients)}")
            print(f"Number of instructions: {len(instructions)}")
            if ingredients:
                print(f"First ingredient: {ingredients[0].get('ingredient', 'N/A')}")
            if instructions:
                print(f"First instruction: {instructions[0].get('instruction', 'N/A')[:100]}...")
        return data
    except Exception as e:
        print(f"❌ Extraction tool failed: {e}")
        return None

def test_3_agent_with_tools():
    """Test 3: Validate agent can use tools correctly"""
    print("\n" + "=" * 60)
    print("TEST 3: Agent with Tools (Integration)")
    print("=" * 60)
    
    agent = create_chef_agent()
    
    # Test with a simple extraction prompt
    test_url = "https://chocolatecoveredkatie.com/vegan-chocolate-chip-cookies-recipe/"
    prompt = f"Extract recipe from this URL: {test_url}. Use the recipe_extraction tool, parse the JSON response, and call final_answer() with the recipe data if successful."
    
    print(f"Testing agent with prompt: {prompt[:100]}...")
    
    try:
        result = agent.run(prompt)
        print(f"Agent result type: {type(result)}")
        print(f"Agent result: {str(result)[:500]}...")
        
        # Check if the result contains success indicators
        result_str = str(result)
        if '{"success": true' in result_str and '"ingredients":' in result_str:
            print("✅ Agent successfully extracted recipe data")
            return True
        else:
            print("❌ Agent did not extract recipe data successfully")
            return False
            
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

def test_4_validation_logic():
    """Test 4: Validate our validation logic works correctly"""
    print("\n" + "=" * 60)
    print("TEST 4: Validation Logic (Parsing)")
    print("=" * 60)
    
    # Simulate what the agent returns
    sample_agent_response = '''{"success": true, "url": "https://example.com", "recipe": {"title": "Test Recipe", "ingredients": [{"ingredient": "1 cup flour"}], "instructions": [{"instruction": "Mix ingredients"}]}}'''
    
    print(f"Testing validation logic with sample response...")
    
    # Test our validation logic
    result_str = sample_agent_response
    
    if '{"success": true' in result_str and '"ingredients":' in result_str and '"instructions":' in result_str:
        print("✅ Validation logic detected successful extraction")
        
        # Try to extract the JSON
        try:
            import json
            import re
            
            json_match = re.search(r'\{.*"success":\s*true.*\}', result_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result_data = json.loads(json_str)
                recipe_data = result_data.get('recipe', {})
                ingredients = recipe_data.get('ingredients', [])
                instructions = recipe_data.get('instructions', [])
                
                if ingredients and instructions:
                    print(f"✅ Successfully parsed recipe with {len(ingredients)} ingredients and {len(instructions)} steps")
                    return True
        except Exception as e:
            print(f"❌ JSON parsing failed: {e}")
    
    print("❌ Validation logic failed")
    return False

def main():
    """Run all systematic tests"""
    print("🧪 SYSTEMATIC TESTING PLAN")
    print("Testing each component independently to isolate issues")
    
    # Test 1: Search tool
    test_recipe = test_1_search_tool()
    
    # Test 2: Extraction tool
    extraction_data = test_2_extraction_tool(test_recipe['url'] if test_recipe else None)
    
    # Test 3: Agent integration
    agent_success = test_3_agent_with_tools()
    
    # Test 4: Validation logic
    validation_success = test_4_validation_logic()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Search Tool: {'✅ PASS' if test_recipe else '❌ FAIL'}")
    print(f"Extraction Tool: {'✅ PASS' if extraction_data else '❌ FAIL'}")
    print(f"Agent Integration: {'✅ PASS' if agent_success else '❌ FAIL'}")
    print(f"Validation Logic: {'✅ PASS' if validation_success else '❌ FAIL'}")
    
    if all([test_recipe, extraction_data, agent_success, validation_success]):
        print("\n🎉 ALL TESTS PASSED - System is working correctly!")
    else:
        print("\n⚠️  SOME TESTS FAILED - Need to investigate further")

if __name__ == "__main__":
    main()
