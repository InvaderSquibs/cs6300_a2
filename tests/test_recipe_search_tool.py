#!/usr/bin/env python3.11
"""
Test script for Recipe Search Tool

Tests the JSON output format, search functionality, and tool behavior.
"""

import sys
import os
import json

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools.recipe_search import RecipeSearchTool

def test_json_format():
    """Test and validate the JSON output format"""
    print("🧪 Testing Recipe Search Tool JSON Format")
    print("=" * 50)
    
    # Create tool instance
    tool = RecipeSearchTool()
    
    # Test with vegan pancakes
    print("1️⃣ Testing with 'vegan pancakes'...")
    result = tool.forward("vegan pancakes")
    
    print("Raw output:")
    print(result)
    print("\n" + "="*50)
    
    # Parse and validate JSON
    try:
        data = json.loads(result)
        print("✅ Valid JSON format")
        print("\nParsed structure:")
        print(json.dumps(data, indent=2))
        
        # Validate required fields
        required_fields = ["success", "query", "recipes", "search_metadata"]
        for field in required_fields:
            if field in data:
                print(f"✅ Contains '{field}' field")
            else:
                print(f"❌ Missing '{field}' field")
        
        # Validate recipe structure
        if "recipes" in data and len(data["recipes"]) > 0:
            recipe = data["recipes"][0]
            recipe_fields = ["id", "title", "url", "description", "source", "extraction_status"]
            for field in recipe_fields:
                if field in recipe:
                    print(f"✅ Recipe contains '{field}'")
                else:
                    print(f"❌ Recipe missing '{field}'")
            
            if "url" in recipe:
                print(f"   URL: {recipe['url']}")
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
    
    print("\n" + "="*50)
    print("🎯 JSON Format Validation Complete")

def test_multiple_dietary_restrictions():
    """Test with various dietary restrictions"""
    print("\n🧪 Testing Multiple Dietary Restrictions")
    print("=" * 50)
    
    tool = RecipeSearchTool()
    test_queries = [
        "vegan pancakes",
        "gluten-free bread",
        "keto cookies",
        "dairy-free smoothie"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i}️⃣ Testing '{query}'...")
        result = tool.forward(query)
        
        try:
            data = json.loads(result)
            if data.get("success") and len(data.get("recipes", [])) > 0:
                recipe = data["recipes"][0]
                print(f"   ✅ Found: {recipe.get('title', 'Unknown')}")
                print(f"   📍 Source: {recipe.get('source', 'Unknown')}")
            else:
                print(f"   ❌ No recipes found")
        except json.JSONDecodeError:
            print(f"   ❌ Invalid JSON response")
        
        print()
    
    print("🎯 Multiple Dietary Restrictions Test Complete")

def test_error_handling():
    """Test error handling with invalid queries"""
    print("\n🧪 Testing Error Handling")
    print("=" * 50)
    
    tool = RecipeSearchTool()
    test_queries = [
        "",  # Empty query
        "xyz123nonexistentrecipe456",  # Nonsensical query
        "a" * 1000,  # Very long query
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i}️⃣ Testing error case: '{query[:50]}{'...' if len(query) > 50 else ''}'")
        result = tool.forward(query)
        
        try:
            data = json.loads(result)
            if "error" in data:
                print(f"   ✅ Properly handled error: {data['error']}")
            elif data.get("success") and len(data.get("recipes", [])) == 0:
                print(f"   ✅ No results found (expected)")
            else:
                print(f"   ⚠️  Unexpected success with invalid query")
        except json.JSONDecodeError:
            print(f"   ❌ Invalid JSON response")
        
        print()
    
    print("🎯 Error Handling Test Complete")

def run_all_tests():
    """Run all tests for Recipe Search Tool"""
    print("🚀 Running All Recipe Search Tool Tests")
    print("=" * 60)
    
    test_json_format()
    test_multiple_dietary_restrictions()
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("🎉 All Recipe Search Tool Tests Complete!")

if __name__ == "__main__":
    run_all_tests()
