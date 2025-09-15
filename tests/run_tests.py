#!/usr/bin/env python3.11
"""
Test Runner for AI Chef Assistant

Runs all tests for the AI Chef Assistant tools.
"""

import sys
import os
import subprocess

def run_test_file(test_file):
    """Run a specific test file"""
    print(f"\n🧪 Running {test_file}...")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), test_file)
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Test passed!")
            print(result.stdout)
        else:
            print("❌ Test failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out!")
        return False
    except Exception as e:
        print(f"💥 Test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Chef Assistant - Test Suite")
    print("=" * 60)
    
    # List of test files
    test_files = [
        "test_recipe_search_tool.py",
        # Add more test files here as we create them
        # "test_recipe_extraction_tool.py",
        # "test_recipe_scaling_tool.py",
    ]
    
    passed = 0
    total = len(test_files)
    
    for test_file in test_files:
        if run_test_file(test_file):
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
