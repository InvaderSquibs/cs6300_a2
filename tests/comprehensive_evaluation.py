#!/usr/bin/env python3.11
"""
Comprehensive Evaluation Script for AI Chef Assistant

This script runs a complete evaluation suite to generate metrics and reports
for the Results & Analysis section of the assignment.
"""

import sys
import os
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class EvaluationMetrics:
    """Class to collect and organize evaluation metrics"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.test_results = {}
        self.tool_metrics = {
            'search': {'success_count': 0, 'total_count': 0, 'avg_results': 0, 'dietary_filtering': 0},
            'extraction': {'success_count': 0, 'total_count': 0, 'avg_ingredients': 0, 'avg_steps': 0},
            'scaling': {'success_count': 0, 'total_count': 0, 'scaling_factors': [], 'unit_conversions': 0},
            'formatter': {'success_count': 0, 'total_count': 0, 'file_sizes': [], 'format_styles': []}
        }
        self.pipeline_metrics = {
            'end_to_end_success': 0,
            'total_pipelines': 0,
            'avg_duration': 0,
            'error_types': []
        }
        self.dietary_restriction_tests = {}
        self.source_link_validation = {}
        
    def add_test_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """Add a test result to the metrics"""
        self.test_results[test_name] = {
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        
    def add_tool_metric(self, tool_name: str, success: bool, metrics: Dict[str, Any]):
        """Add tool-specific metrics"""
        if tool_name in self.tool_metrics:
            self.tool_metrics[tool_name]['total_count'] += 1
            if success:
                self.tool_metrics[tool_name]['success_count'] += 1
                
            # Add specific metrics
            for key, value in metrics.items():
                if key in self.tool_metrics[tool_name]:
                    if isinstance(self.tool_metrics[tool_name][key], list):
                        self.tool_metrics[tool_name][key].append(value)
                    else:
                        self.tool_metrics[tool_name][key] = value
                        
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive evaluation report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        # Calculate success rates
        for tool, metrics in self.tool_metrics.items():
            if metrics['total_count'] > 0:
                metrics['success_rate'] = metrics['success_count'] / metrics['total_count']
            else:
                metrics['success_rate'] = 0
                
        # Calculate pipeline success rate
        if self.pipeline_metrics['total_pipelines'] > 0:
            self.pipeline_metrics['success_rate'] = (
                self.pipeline_metrics['end_to_end_success'] / 
                self.pipeline_metrics['total_pipelines']
            )
        else:
            self.pipeline_metrics['success_rate'] = 0
            
        return {
            'evaluation_metadata': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'total_duration_seconds': total_duration,
                'evaluation_version': '1.0'
            },
            'test_results': self.test_results,
            'tool_metrics': self.tool_metrics,
            'pipeline_metrics': self.pipeline_metrics,
            'dietary_restriction_tests': self.dietary_restriction_tests,
            'source_link_validation': self.source_link_validation,
            'summary': {
                'total_tests': len(self.test_results),
                'successful_tests': sum(1 for r in self.test_results.values() if r['success']),
                'overall_success_rate': sum(1 for r in self.test_results.values() if r['success']) / len(self.test_results) if self.test_results else 0
            }
        }

def run_command_with_metrics(command: str, timeout: int = 180) -> tuple:
    """Run a command and return success, stdout, stderr, and execution time"""
    start_time = time.time()
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        execution_time = time.time() - start_time
        return result.returncode == 0, result.stdout, result.stderr, execution_time
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        return False, "", "Command timed out", execution_time
    except Exception as e:
        execution_time = time.time() - start_time
        return False, "", str(e), execution_time

def test_basic_recipe_search(metrics: EvaluationMetrics):
    """Test 1: Basic Recipe Search Functionality"""
    print("🔍 Test 1: Basic Recipe Search")
    print("-" * 40)
    
    command = 'python3.11 src/chef_agent.py "I want some pancakes"'
    success, stdout, stderr, duration = run_command_with_metrics(command)
    
    # Extract metrics from output
    search_metrics = {
        'duration': duration,
        'has_search_results': 'Search Results:' in stdout,
        'has_extraction': 'Recipe extraction' in stdout or 'Step 2' in stdout,
        'has_formatting': 'Recipe formatted successfully' in stdout or 'results/recipes/' in stdout,
        'has_source_link': 'Source' in stdout or 'Original Recipe URL' in stdout
    }
    
    # Count search results
    if 'Search Results:' in stdout:
        lines = stdout.split('\n')
        for line in lines:
            if 'Search Results:' in line:
                # Look for recipe count in next few lines
                for i in range(1, 10):
                    if i < len(lines) and ('recipe' in lines[i].lower() or 'found' in lines[i].lower()):
                        search_metrics['result_count'] = lines[i]
                        break
    
    metrics.add_test_result('basic_recipe_search', success, search_metrics)
    metrics.add_tool_metric('search', success, search_metrics)
    
    if success:
        print(f"✅ Basic search test passed ({duration:.2f}s)")
        print(f"   📊 Search results found: {search_metrics.get('has_search_results', False)}")
        print(f"   📊 Extraction completed: {search_metrics.get('has_extraction', False)}")
        print(f"   📊 Formatting completed: {search_metrics.get('has_formatting', False)}")
        print(f"   📊 Source link included: {search_metrics.get('has_source_link', False)}")
    else:
        print(f"❌ Basic search test failed: {stderr}")
    
    return success

def test_dietary_restriction_handling(metrics: EvaluationMetrics):
    """Test 2: Dietary Restriction Processing"""
    print("\n🥗 Test 2: Dietary Restriction Handling")
    print("-" * 40)
    
    # Test with explicit restrictions
    command1 = 'python3.11 src/chef_agent.py "I want some cookies" --restrictions "vegan"'
    success1, stdout1, stderr1, duration1 = run_command_with_metrics(command1)
    
    # Test with natural language extraction
    command2 = 'python3.11 src/chef_agent.py "I want some pancakes for my keto friend"'
    success2, stdout2, stderr2, duration2 = run_command_with_metrics(command2)
    
    # Extract dietary restriction metrics
    dietary_metrics = {
        'explicit_restrictions_success': success1,
        'natural_language_extraction_success': success2,
        'explicit_duration': duration1,
        'extraction_duration': duration2,
        'vegan_filtering_detected': 'vegan' in stdout1.lower(),
        'keto_extraction_detected': 'keto' in stdout2.lower()
    }
    
    metrics.add_test_result('dietary_restriction_handling', success1 and success2, dietary_metrics)
    metrics.dietary_restriction_tests = dietary_metrics
    
    if success1 and success2:
        print(f"✅ Dietary restriction tests passed")
        print(f"   📊 Explicit restrictions: {success1} ({duration1:.2f}s)")
        print(f"   📊 Natural language extraction: {success2} ({duration2:.2f}s)")
        print(f"   📊 Vegan filtering detected: {dietary_metrics['vegan_filtering_detected']}")
        print(f"   📊 Keto extraction detected: {dietary_metrics['keto_extraction_detected']}")
    else:
        print(f"❌ Dietary restriction tests failed")
        print(f"   Explicit: {success1}, Extraction: {success2}")
    
    return success1 and success2

def test_recipe_scaling(metrics: EvaluationMetrics):
    """Test 3: Recipe Scaling Functionality"""
    print("\n⚖️ Test 3: Recipe Scaling")
    print("-" * 40)
    
    command = 'python3.11 src/chef_agent.py "I want some pancakes for 8 people"'
    success, stdout, stderr, duration = run_command_with_metrics(command)
    
    # Extract scaling metrics
    scaling_metrics = {
        'duration': duration,
        'scaling_detected': 'scaling' in stdout.lower() or '8 people' in stdout,
        'has_scaling_factor': 'scaling factor' in stdout.lower() or 'factor' in stdout.lower(),
        'has_unit_conversions': 'conversion' in stdout.lower() or 'unit' in stdout.lower()
    }
    
    # Look for scaling information in output
    if 'scaling' in stdout.lower():
        lines = stdout.split('\n')
        for line in lines:
            if 'scaling' in line.lower() and ('factor' in line.lower() or 'servings' in line.lower()):
                scaling_metrics['scaling_details'] = line.strip()
                break
    
    metrics.add_test_result('recipe_scaling', success, scaling_metrics)
    metrics.add_tool_metric('scaling', success, scaling_metrics)
    
    if success:
        print(f"✅ Recipe scaling test passed ({duration:.2f}s)")
        print(f"   📊 Scaling detected: {scaling_metrics['scaling_detected']}")
        print(f"   📊 Scaling factor found: {scaling_metrics['has_scaling_factor']}")
        print(f"   📊 Unit conversions: {scaling_metrics['has_unit_conversions']}")
    else:
        print(f"❌ Recipe scaling test failed: {stderr}")
    
    return success

def test_full_pipeline_with_formatting(metrics: EvaluationMetrics):
    """Test 4: Full Pipeline with Formatting"""
    print("\n📝 Test 4: Full Pipeline with Formatting")
    print("-" * 40)
    
    command = 'python3.11 src/chef_agent.py "I want some vegan chocolate chip cookies for 6 people" --restrictions "vegan"'
    success, stdout, stderr, duration = run_command_with_metrics(command)
    
    # Extract comprehensive pipeline metrics
    pipeline_metrics = {
        'duration': duration,
        'search_completed': 'Search Results:' in stdout or 'Step 1' in stdout,
        'extraction_completed': 'Recipe extraction' in stdout or 'Step 2' in stdout,
        'scaling_completed': 'scaling' in stdout.lower() or 'Step 3' in stdout,
        'formatting_completed': 'Recipe formatted successfully' in stdout or 'results/recipes/' in stdout,
        'source_link_included': 'Source' in stdout or 'Original Recipe URL' in stdout,
        'file_generated': 'results/recipes/' in stdout
    }
    
    # Extract file information
    if 'results/recipes/' in stdout:
        lines = stdout.split('\n')
        for line in lines:
            if 'results/recipes/' in line:
                pipeline_metrics['generated_file'] = line.strip()
                break
    
    # Count pipeline steps
    step_count = 0
    for i in range(1, 10):
        if f'Step {i}' in stdout:
            step_count += 1
        else:
            break
    pipeline_metrics['pipeline_steps'] = step_count
    
    metrics.add_test_result('full_pipeline_formatting', success, pipeline_metrics)
    metrics.pipeline_metrics['total_pipelines'] += 1
    if success:
        metrics.pipeline_metrics['end_to_end_success'] += 1
    
    if success:
        print(f"✅ Full pipeline test passed ({duration:.2f}s)")
        print(f"   📊 Pipeline steps: {pipeline_metrics['pipeline_steps']}")
        print(f"   📊 Search: {pipeline_metrics['search_completed']}")
        print(f"   📊 Extraction: {pipeline_metrics['extraction_completed']}")
        print(f"   📊 Scaling: {pipeline_metrics['scaling_completed']}")
        print(f"   📊 Formatting: {pipeline_metrics['formatting_completed']}")
        print(f"   📊 Source link: {pipeline_metrics['source_link_included']}")
        print(f"   📊 File generated: {pipeline_metrics['file_generated']}")
    else:
        print(f"❌ Full pipeline test failed: {stderr}")
    
    return success

def test_error_handling(metrics: EvaluationMetrics):
    """Test 5: Error Handling and Graceful Degradation"""
    print("\n⚠️ Test 5: Error Handling")
    print("-" * 40)
    
    # Test with invalid query
    command = 'python3.11 src/chef_agent.py "xyz123nonexistentrecipe456"'
    success, stdout, stderr, duration = run_command_with_metrics(command)
    
    # Extract error handling metrics
    error_metrics = {
        'duration': duration,
        'graceful_error_handling': 'error' in stdout.lower() or 'not found' in stdout.lower() or 'failed' in stdout.lower(),
        'no_crash': not ('traceback' in stderr.lower() or 'exception' in stderr.lower()),
        'helpful_error_message': len(stdout.strip()) > 0
    }
    
    metrics.add_test_result('error_handling', error_metrics['graceful_error_handling'] and error_metrics['no_crash'], error_metrics)
    
    if error_metrics['graceful_error_handling'] and error_metrics['no_crash']:
        print(f"✅ Error handling test passed ({duration:.2f}s)")
        print(f"   📊 Graceful error handling: {error_metrics['graceful_error_handling']}")
        print(f"   📊 No crash: {error_metrics['no_crash']}")
        print(f"   📊 Helpful message: {error_metrics['helpful_error_message']}")
    else:
        print(f"❌ Error handling test failed")
        print(f"   Graceful: {error_metrics['graceful_error_handling']}, No crash: {error_metrics['no_crash']}")
    
    return error_metrics['graceful_error_handling'] and error_metrics['no_crash']

def validate_source_links(metrics: EvaluationMetrics):
    """Validate that generated recipes have source links"""
    print("\n🔗 Test 6: Source Link Validation")
    print("-" * 40)
    
    recipes_dir = "results/recipes"
    source_link_metrics = {
        'total_files': 0,
        'files_with_source_links': 0,
        'source_link_format_correct': 0,
        'files_checked': []
    }
    
    if os.path.exists(recipes_dir):
        for filename in os.listdir(recipes_dir):
            if filename.endswith('.md'):
                file_path = os.path.join(recipes_dir, filename)
                source_link_metrics['total_files'] += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    file_info = {
                        'filename': filename,
                        'has_source_section': '## Source' in content,
                        'has_url_link': 'http' in content and '](' in content,
                        'file_size': len(content)
                    }
                    
                    source_link_metrics['files_checked'].append(file_info)
                    
                    if file_info['has_source_section'] and file_info['has_url_link']:
                        source_link_metrics['files_with_source_links'] += 1
                        source_link_metrics['source_link_format_correct'] += 1
                        
                except Exception as e:
                    print(f"   ⚠️ Error reading {filename}: {e}")
    
    metrics.source_link_validation = source_link_metrics
    metrics.add_test_result('source_link_validation', 
                          source_link_metrics['files_with_source_links'] > 0, 
                          source_link_metrics)
    
    if source_link_metrics['total_files'] > 0:
        success_rate = source_link_metrics['files_with_source_links'] / source_link_metrics['total_files']
        print(f"✅ Source link validation completed")
        print(f"   📊 Total recipe files: {source_link_metrics['total_files']}")
        print(f"   📊 Files with source links: {source_link_metrics['files_with_source_links']}")
        print(f"   📊 Success rate: {success_rate:.2%}")
    else:
        print(f"⚠️ No recipe files found for source link validation")
    
    return source_link_metrics['files_with_source_links'] > 0

def run_comprehensive_evaluation():
    """Run the complete evaluation suite"""
    print("🧪 AI Chef Assistant - Comprehensive Evaluation Suite")
    print("=" * 60)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    metrics = EvaluationMetrics()
    
    # Run all tests
    tests = [
        ("Basic Recipe Search", test_basic_recipe_search),
        ("Dietary Restriction Handling", test_dietary_restriction_handling),
        ("Recipe Scaling", test_recipe_scaling),
        ("Full Pipeline with Formatting", test_full_pipeline_with_formatting),
        ("Error Handling", test_error_handling),
        ("Source Link Validation", validate_source_links)
    ]
    
    for test_name, test_func in tests:
        try:
            test_func(metrics)
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            metrics.add_test_result(test_name.lower().replace(' ', '_'), False, {'error': str(e)})
    
    # Generate comprehensive report
    report = metrics.generate_report()
    
    # Save report to results/reports
    os.makedirs('results/reports', exist_ok=True)
    report_filename = f"results/reports/comprehensive_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 EVALUATION SUMMARY")
    print("=" * 60)
    
    total_tests = len(metrics.test_results)
    successful_tests = sum(1 for r in metrics.test_results.values() if r['success'])
    success_rate = successful_tests / total_tests if total_tests > 0 else 0
    
    print(f"🎯 Overall Success Rate: {success_rate:.2%} ({successful_tests}/{total_tests})")
    print(f"📁 Report saved to: {report_filename}")
    
    # Tool-specific metrics
    print("\n🔧 Tool Performance:")
    for tool, tool_metrics in metrics.tool_metrics.items():
        if tool_metrics['total_count'] > 0:
            success_rate = tool_metrics['success_count'] / tool_metrics['total_count']
            print(f"   {tool.title()}: {success_rate:.2%} ({tool_metrics['success_count']}/{tool_metrics['total_count']})")
    
    # Pipeline metrics
    if metrics.pipeline_metrics['total_pipelines'] > 0:
        pipeline_success = metrics.pipeline_metrics['end_to_end_success'] / metrics.pipeline_metrics['total_pipelines']
        print(f"\n🔄 Pipeline Success Rate: {pipeline_success:.2%}")
    
    print(f"\n⏱️ Total Evaluation Time: {report['evaluation_metadata']['total_duration_seconds']:.2f} seconds")
    
    return report

if __name__ == "__main__":
    report = run_comprehensive_evaluation()
    sys.exit(0 if report['summary']['overall_success_rate'] > 0.8 else 1)
