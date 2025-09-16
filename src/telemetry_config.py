#!/usr/bin/env python3.11
"""
Phoenix Telemetry Configuration for AI Chef Assistant

This module provides easy telemetry configuration for monitoring
the AI Chef Assistant's tool execution and performance.

Features:
- Automatic telemetry setup with Phoenix server
- Environment variable configuration
- Comprehensive metrics tracking for all 4 tools
- Real-time monitoring and debugging capabilities

Usage:
    # Enable telemetry by importing this module
    from telemetry_config import enable_telemetry
    enable_telemetry()
    
    # Or set environment variable
    export ENABLE_TELEMETRY=true
    
    # Start Phoenix server
    python3.11 -m phoenix.server.main serve --port 6006
    
    # View metrics at http://localhost:6006

Tracked Metrics:
- Search Tool: query, results_count, dietary_restrictions, filtered_count
- Extraction Tool: url, ingredients_count, instructions_count, servings, timing
- Scaling Tool: original_servings, target_servings, scaling_factor, unit_conversions
- Formatter Tool: recipe_title, filename, file_size, format_style
- Pipeline: total_duration, tool_sequence, success_rate, error_types
"""

import os
from typing import Optional

def enable_telemetry(project_name: str = "ai-chef-assistant", 
                    endpoint: str = "http://localhost:6006/v1/traces") -> bool:
    """
    Enable Phoenix telemetry for the AI Chef Assistant.
    
    Args:
        project_name: Name of the project in Phoenix dashboard
        endpoint: Phoenix server endpoint
        
    Returns:
        bool: True if telemetry was successfully enabled, False otherwise
    """
    try:
        from phoenix.otel import register
        from openinference.instrumentation.smolagents import SmolagentsInstrumentor
        
        print(f"🔍 Enabling Phoenix telemetry for project: {project_name}")
        print(f"📊 Phoenix endpoint: {endpoint}")
        
        # Register Phoenix telemetry
        register(
            endpoint=endpoint,
            project_name=project_name
        )
        
        # Instrument smolagents
        SmolagentsInstrumentor().instrument()
        
        print("✅ Phoenix telemetry enabled successfully!")
        print("📈 Metrics will be tracked for:")
        print("   - Recipe Search Tool")
        print("   - Recipe Extraction Tool") 
        print("   - Recipe Scaling Tool")
        print("   - Recipe Formatter Tool")
        print("   - Agent execution flow")
        print("   - Tool call timing and success rates")
        print("   - Custom scaling factors and extraction metrics")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to enable telemetry - missing dependencies: {e}")
        print("💡 Install with: pip install 'smolagents[telemetry]' opentelemetry-sdk openinference-instrumentation-smolagents")
        return False
    except Exception as e:
        print(f"❌ Failed to enable telemetry: {e}")
        return False

def is_telemetry_enabled() -> bool:
    """
    Check if telemetry is enabled via environment variable.
    
    Returns:
        bool: True if ENABLE_TELEMETRY environment variable is set to 'true'
    """
    return os.getenv('ENABLE_TELEMETRY', '').lower() == 'true'

def auto_enable_telemetry() -> bool:
    """
    Automatically enable telemetry if ENABLE_TELEMETRY environment variable is set.
    
    Returns:
        bool: True if telemetry was enabled, False otherwise
    """
    if is_telemetry_enabled():
        return enable_telemetry()
    return False

# Auto-enable if environment variable is set
if is_telemetry_enabled():
    auto_enable_telemetry()
