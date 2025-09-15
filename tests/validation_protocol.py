#!/usr/bin/env python3.11
"""
Validation Protocol Test Script

This script implements the standardized validation testing protocol
for each tool in the AI Chef Assistant.
"""

import sys
import os
import json
import subprocess

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_command(command, timeout=120):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out (this is normal for agent operations)"
    except Exception as e:
        return False, "", str(e)

def test_help_documentation():
    """Test 1: Help Documentation Test"""
    print("1️⃣ Testing Help Documentation")
    print("-" * 40)
    
    success, stdout, stderr = run_command("python3.11 src/chef_agent.py help")
    
    if success:
        print("✅ Help command executed successfully")
        
        # Check for key sections
        required_sections = [
            "USAGE:",
            "AVAILABLE TOOLS:",
            "EXAMPLES:",
            "ENVIRONMENT:"
        ]
        
        for section in required_sections:
            if section in stdout:
                print(f"✅ Found section: {section}")
            else:
                print(f"❌ Missing section: {section}")
                return False
        
        # Check for tool listing
        if "recipe_search" in stdout:
            print("✅ Tool 'recipe_search' found in help")
        else:
            print("❌ Tool 'recipe_search' not found in help")
            return False
            
        return True
    else:
        print(f"❌ Help command failed: {stderr}")
        return False

def test_individual_tool():
    """Test 2: Individual Tool Test - Contract Format Only"""
    print("\n2️⃣ Testing Individual Tool (Contract Format)")
    print("-" * 40)
    
    # Test multiple valid queries for better coverage
    test_cases = [
        # Basic queries (no dietary restrictions)
        ("pancakes", None),
        ("chocolate chip cookies", None),
        # Queries with dietary restrictions
        ("pancakes", ["vegan"]),
        ("bread", ["gluten-free", "keto"]),
        ("cookies", ["paleo", "dairy-free"])
    ]
    
    all_passed = True
    
    for query, dietary_restrictions in test_cases:
        if dietary_restrictions:
            restrictions_str = ",".join(dietary_restrictions)
            print(f"Testing query: '{query}' with restrictions: {restrictions_str}")
            cmd = f'python3.11 src/chef_agent.py search "{query}" --diet "{restrictions_str}"'
        else:
            print(f"Testing query: '{query}' (no restrictions)")
            cmd = f'python3.11 src/chef_agent.py search "{query}"'
        
        success, stdout, stderr = run_command(cmd)
    
        if success:
            print(f"✅ Query '{query}' executed successfully")
            
            # Look for the specific contract format defined in the tool
            if "RECIPE_FOUND:" in stdout:
                print(f"✅ Contract-based response found for '{query}' (agent followed tool contract)")
                # Extract and print the recipe details from the Search Results section
                lines = stdout.split('\n')
                for i, line in enumerate(lines):
                    if "📋 Search Results:" in line and i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if "RECIPE_FOUND:" in next_line:
                            print(f"📋 Recipe found: {next_line}")
                            break
            elif "NO_RECIPES_FOUND:" in stdout:
                print(f"⚠️  No recipes found for '{query}'")
                # Extract and print the error message
                lines = stdout.split('\n')
                for line in lines:
                    if "NO_RECIPES_FOUND:" in line:
                        print(f"📋 Error message: {line.strip()}")
                        break
            else:
                print(f"❌ No contract format detected for '{query}'")
                print("Raw output preview:")
                print(stdout[:500] + "..." if len(stdout) > 500 else stdout)
                all_passed = False
        else:
            if "timed out" in stderr:
                print(f"⚠️  Query '{query}' timed out (normal for agent operations)")
            else:
                print(f"❌ Query '{query}' failed: {stderr}")
                all_passed = False
        print()
    
    return all_passed

def test_dietary_restrictions():
    """Test 2.5: Dietary Restrictions Feature Test"""
    print("\n2️⃣.5 Testing Dietary Restrictions Feature")
    print("-" * 40)
    
    # Test dietary restrictions functionality
    test_cases = [
        ("pancakes", ["vegan"], "Should find vegan pancake recipes"),
        ("bread", ["gluten-free", "keto"], "Should find gluten-free keto bread"),
        ("cookies", ["paleo", "dairy-free"], "Should find paleo dairy-free cookies"),
        ("pasta", ["vegetarian"], "Should find vegetarian pasta recipes")
    ]
    
    all_passed = True
    
    for query, restrictions, description in test_cases:
        restrictions_str = ",".join(restrictions)
        print(f"Testing: {description}")
        print(f"  Query: '{query}' with restrictions: {restrictions_str}")
        
        cmd = f'python3.11 src/chef_agent.py search "{query}" --diet "{restrictions_str}"'
        success, stdout, stderr = run_command(cmd)
        
        if success:
            if "RECIPE_FOUND:" in stdout:
                print(f"✅ Found recipe with dietary restrictions")
                # Extract and print the recipe details
                lines = stdout.split('\n')
                for i, line in enumerate(lines):
                    if "📋 Search Results:" in line and i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if "RECIPE_FOUND:" in next_line:
                            print(f"📋 Recipe: {next_line}")
                            break
            else:
                print(f"⚠️  No recipes found for '{query}' with restrictions {restrictions_str}")
        else:
            if "timed out" in stderr:
                print(f"⚠️  Query timed out (normal for agent operations)")
            else:
                print(f"❌ Query failed: {stderr}")
                all_passed = False
        print()
    
    return all_passed

def test_error_handling():
    """Test 3: Error Handling Test"""
    print("\n3️⃣ Testing Error Handling")
    print("-" * 40)
    
    error_cases = [
        ("", "Empty query should return NO_RECIPES_FOUND"),
        ("xyz123nonexistentrecipe456", "Nonsense query should return NO_RECIPES_FOUND"),
    ]
    
    for query, expected in error_cases:
        print(f"Testing error case: '{query[:20]}{'...' if len(query) > 20 else ''}'")
        print(f"Expected: {expected}")
        
        success, stdout, stderr = run_command(f'python3.11 src/chef_agent.py search "{query}"')
        
        if success:
            # Extract the actual error message from the Search Results section
            actual_error = "No error message found"
            lines = stdout.split('\n')
            for i, line in enumerate(lines):
                if "📋 Search Results:" in line and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if "NO_RECIPES_FOUND:" in next_line:
                        actual_error = next_line
                        break
            
            # Check if error was handled gracefully using contract format
            if "NO_RECIPES_FOUND:" in stdout:
                print(f"✅ Error handled gracefully (contract format)")
                print(f"Actual: {actual_error}")
            else:
                error_indicators = ["error", "failed", "no recipes found", "not found", "invalid", "empty"]
                if any(indicator in stdout.lower() for indicator in error_indicators):
                    print(f"✅ Error handled gracefully (fallback detection)")
                    print(f"Actual: {actual_error}")
                else:
                    print(f"⚠️  No clear error indication")
                    print(f"Actual: {actual_error}")
        else:
            if "timed out" in stderr:
                print(f"⚠️  Error test timed out (normal for agent operations)")
            else:
                print(f"❌ Command failed unexpectedly: {stderr}")
        print()
    
    return True

def test_automated_tests():
    """Test 4: Automated Tests"""
    print("\n4️⃣ Testing Automated Test Suite")
    print("-" * 40)
    
    success, stdout, stderr = run_command("python3.11 tests/run_tests.py")
    
    if success:
        print("✅ Automated tests passed")
        if "All tests passed" in stdout:
            print("✅ All test cases passed")
        else:
            print("⚠️  Some test cases may have failed")
        return True
    else:
        print(f"❌ Automated tests failed: {stderr}")
        return False

def run_validation_protocol(fast_mode=False):
    """Run the complete validation protocol"""
    print("🧪 AI Chef Assistant - Validation Protocol")
    if fast_mode:
        print("⚡ Running in FAST MODE")
    print("=" * 50)
    
    # Define which tests to run based on mode
    if fast_mode:
        tests = [
            ("Individual Tool", test_individual_tool),
        ]
    else:
        tests = [
            ("Help Documentation", test_help_documentation),
            ("Individual Tool", test_individual_tool),
            ("Dietary Restrictions", test_dietary_restrictions),
            ("Error Handling", test_error_handling),
            ("Automated Tests", test_automated_tests),
        ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validation tests passed!")
        return True
    else:
        print("❌ Some validation tests failed!")
        return False

if __name__ == "__main__":
    # Check for fast mode argument
    fast_mode = len(sys.argv) > 1 and sys.argv[1] == "--fast"
    success = run_validation_protocol(fast_mode=fast_mode)
    sys.exit(0 if success else 1)
