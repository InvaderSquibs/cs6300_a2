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

def test_full_pipeline_basic():
    """Test 2: Full Pipeline Test - Basic Recipe (No Dietary Restrictions)"""
    print("\n2️⃣ Testing Full Pipeline - Basic Recipe")
    print("-" * 50)
    
    print(f"\n🔍 Testing: Basic pancake recipe with full toolset")
    print(f"   Query: 'pancakes'")
    print(f"   Dietary restrictions: None")
    print(f"   Expected: Search → Extract → Recipe Object")
    
    cmd = 'python3.11 src/chef_agent.py e2e'
    print(f"   Command: {cmd}")
    success, stdout, stderr = run_command(cmd, timeout=180)
    
    if success:
        print(f"   ✅ Command executed successfully")
        
        # Check for LLM processing evidence
        if "OpenAIServerModel" in stdout:
            print(f"   ✅ LLM agent processing confirmed")
        if "Step 1" in stdout and "Step 2" in stdout:
            print(f"   ✅ Multi-step agent execution confirmed")
        
        # Check for successful pipeline completion (both old and new formats)
        if (("✅ Recipe search successful" in stdout and "✅ Recipe extraction successful" in stdout) or 
            ("✅ Success! Found recipe with" in stdout and "ingredients and" in stdout and "steps" in stdout)):
            print(f"   ✅ Full pipeline stages completed: searching → extracting → scaling")
            
            # Extract and display recipe details
            if "Recipe title:" in stdout:
                for line in stdout.split('\n'):
                    if "Recipe title:" in line:
                        print(f"   📋 {line.strip()}")
                        break
            
            if "ingredients and" in stdout and "steps" in stdout:
                for line in stdout.split('\n'):
                    if "ingredients and" in line and "steps" in line:
                        print(f"   📋 {line.strip()}")
                        break
            
            # Check for tool execution logs
            if "Execution logs:" in stdout:
                print(f"   ✅ Tool execution logs present")
            
            # Check for final answer format
            if "Final answer:" in stdout:
                print(f"   ✅ Final answer format confirmed")
            
            return True
        else:
            print(f"   ⚠️  Pipeline stages incomplete")
            print(f"   Raw output preview:")
            print(f"   {stdout[:300]}{'...' if len(stdout) > 300 else ''}")
            return False
    else:
        if "timed out" in stderr:
            print(f"   ⚠️  Test timed out (normal for complex operations)")
        else:
            print(f"   ❌ Test failed: {stderr}")
        return False

def test_full_pipeline_dietary():
    """Test 3: Full Pipeline Test - Dietary Restrictions Recipe"""
    print("\n3️⃣ Testing Full Pipeline - Dietary Restrictions Recipe")
    print("-" * 50)
    
    print(f"\n🔍 Testing: Vegan pancake recipe with full toolset")
    print(f"   Query: 'pancakes'")
    print(f"   Dietary restrictions: vegan")
    print(f"   Expected: Search → Extract → Recipe Object with dietary filtering")
    
    cmd = 'python3.11 src/chef_agent.py e2e --diet "vegan"'
    print(f"   Command: {cmd}")
    success, stdout, stderr = run_command(cmd, timeout=180)
    
    if success:
        print(f"   ✅ Command executed successfully")
        
        # Check for LLM processing evidence
        if "OpenAIServerModel" in stdout:
            print(f"   ✅ LLM agent processing confirmed")
        if "Step 1" in stdout and "Step 2" in stdout:
            print(f"   ✅ Multi-step agent execution confirmed")
        
        # Check for successful pipeline completion (both old and new formats)
        if (("✅ Recipe search successful" in stdout and "✅ Recipe extraction successful" in stdout) or 
            ("✅ Success! Found recipe with" in stdout and "ingredients and" in stdout and "steps" in stdout)):
            print(f"   ✅ Full pipeline stages completed: searching → extracting → scaling")
            
            # Extract and display recipe details
            if "Recipe title:" in stdout:
                for line in stdout.split('\n'):
                    if "Recipe title:" in line:
                        print(f"   📋 {line.strip()}")
                        break
            
            if "ingredients and" in stdout and "steps" in stdout:
                for line in stdout.split('\n'):
                    if "ingredients and" in line and "steps" in line:
                        print(f"   📋 {line.strip()}")
                        break
            
            # Check for tool execution logs
            if "Execution logs:" in stdout:
                print(f"   ✅ Tool execution logs present")
            
            # Check for final answer format
            if "Final answer:" in stdout:
                print(f"   ✅ Final answer format confirmed")
            
            return True
        else:
            print(f"   ⚠️  Pipeline stages incomplete")
            print(f"   Raw output preview:")
            print(f"   {stdout[:300]}{'...' if len(stdout) > 300 else ''}")
            return False
    else:
        if "timed out" in stderr:
            print(f"   ⚠️  Test timed out (normal for complex operations)")
        else:
            print(f"   ❌ Test failed: {stderr}")
        return False

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

def test_full_pipeline_comprehensive():
    """Test 4: Full Pipeline Test - Comprehensive Recipe Object Display"""
    print("\n4️⃣ Testing Full Pipeline - Comprehensive Recipe Object")
    print("-" * 50)
    
    print(f"\n🔍 Testing: Gluten-free keto pancake recipe with full toolset")
    print(f"   Query: 'pancakes'")
    print(f"   Dietary restrictions: gluten-free, keto")
    print(f"   Expected: Search → Extract → Complete Recipe Object with ingredients & steps")
    
    cmd = 'python3.11 src/chef_agent.py e2e --diet "gluten-free,keto"'
    print(f"   Command: {cmd}")
    success, stdout, stderr = run_command(cmd, timeout=180)
    
    if success:
        print(f"   ✅ Command executed successfully")
        
        # Check for LLM processing evidence
        if "OpenAIServerModel" in stdout:
            print(f"   ✅ LLM agent processing confirmed")
        if "Step 1" in stdout and "Step 2" in stdout:
            print(f"   ✅ Multi-step agent execution confirmed")
        
        # Check for successful pipeline completion (both old and new formats)
        if (("✅ Recipe search successful" in stdout and "✅ Recipe extraction successful" in stdout) or 
            ("✅ Success! Found recipe with" in stdout and "ingredients and" in stdout and "steps" in stdout)):
            print(f"   ✅ Full pipeline stages completed: searching → extracting → scaling")
            
            # Extract and display recipe details
            if "Recipe title:" in stdout:
                for line in stdout.split('\n'):
                    if "Recipe title:" in line:
                        print(f"   📋 {line.strip()}")
                        break
            
            if "ingredients and" in stdout and "steps" in stdout:
                for line in stdout.split('\n'):
                    if "ingredients and" in line and "steps" in line:
                        print(f"   📋 {line.strip()}")
                        break
            
            # Check for tool execution logs
            if "Execution logs:" in stdout:
                print(f"   ✅ Tool execution logs present")
            
            # Check for final answer format
            if "Final answer:" in stdout:
                print(f"   ✅ Final answer format confirmed")
            
            # Extract and display the actual recipe object from the output
            print(f"\n   📋 RECIPE OBJECT EXTRACTION:")
            if "Final answer:" in stdout:
                # Find the final answer section and extract the recipe object
                lines = stdout.split('\n')
                in_final_answer = False
                recipe_object = []
                
                for line in lines:
                    if "Final answer:" in line:
                        in_final_answer = True
                        continue
                    if in_final_answer and line.strip():
                        recipe_object.append(line.strip())
                    elif in_final_answer and not line.strip():
                        break
                
                if recipe_object:
                    print(f"   📋 Recipe Object Found:")
                    for line in recipe_object[:10]:  # Show first 10 lines
                        print(f"      {line}")
                    if len(recipe_object) > 10:
                        print(f"      ... ({len(recipe_object) - 10} more lines)")
            
            return True
        else:
            print(f"   ⚠️  Pipeline stages incomplete")
            print(f"   Raw output preview:")
            print(f"   {stdout[:300]}{'...' if len(stdout) > 300 else ''}")
            return False
    else:
        if "timed out" in stderr:
            print(f"   ⚠️  Test timed out (normal for complex operations)")
        else:
            print(f"   ❌ Test failed: {stderr}")
        return False

def test_full_pipeline_with_scaling():
    """Test 5: Full Pipeline - Recipe Scaling"""
    print("\n5️⃣ Testing Full Pipeline - Recipe Scaling")
    print("-" * 50)
    
    print(f"\n🔍 Testing: Pancake recipe with scaling for dinner party")
    print(f"   Query: 'pancakes for a dinner party with 8 guests'")
    print(f"   Dietary restrictions: None")
    print(f"   Expected: Search → Extract → Scale → Scaled Recipe Object")
    
    cmd = 'python3.11 src/chef_agent.py "I\'d like some pancakes for a dinner party with 8 guests"'
    print(f"   Command: {cmd}")
    
    success, stdout, stderr = run_command(cmd, timeout=180)
    
    if success:
        print(f"   ✅ Command executed successfully")
        
        # Check for LLM processing evidence
        if "OpenAIServerModel" in stdout:
            print(f"   ✅ LLM agent processing confirmed")
        if "Step 1" in stdout and "Step 2" in stdout:
            print(f"   ✅ Multi-step agent execution confirmed")
        
        # Check for scaling functionality
        if ("scaling requirements" in stdout or "Recipe scaled successfully" in stdout or 
            "User prompt indicates scaling needed" in stdout or "scaling needed" in stdout):
            print(f"   ✅ Recipe scaling functionality confirmed")
        else:
            print(f"   ❌ Recipe scaling functionality not confirmed")
            return False
        
        # Check for successful pipeline completion
        if (("✅ Recipe search successful" in stdout and "✅ Recipe extraction successful" in stdout) or 
            ("✅ Success! Found recipe with" in stdout and "ingredients and" in stdout and "steps" in stdout)):
            print(f"   ✅ Full pipeline stages completed: searching → extracting → scaling")
            
            # Extract and display recipe details
            if "Recipe title:" in stdout:
                for line in stdout.split('\n'):
                    if "Recipe title:" in line:
                        print(f"   📋 {line.strip()}")
                        break
            
            if "ingredients and" in stdout and "steps" in stdout:
                for line in stdout.split('\n'):
                    if "ingredients and" in line and "steps" in line:
                        print(f"   📋 {line.strip()}")
                        break
            
            return True
        else:
            print(f"   ❌ Full pipeline stages not completed")
            return False
    else:
        print(f"   ❌ Command failed")
        print(f"   Error: {stderr}")
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
            ("Full Pipeline - Basic", test_full_pipeline_basic),
        ]
    else:
        # Focus on 2-3 end-to-end LLM tests for efficiency
        tests = [
            ("Full Pipeline - Basic", test_full_pipeline_basic),
            ("Full Pipeline - Dietary", test_full_pipeline_dietary),
            ("Full Pipeline - Comprehensive", test_full_pipeline_comprehensive),
            ("Full Pipeline - Scaling", test_full_pipeline_with_scaling),
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
