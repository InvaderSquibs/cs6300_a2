#!/usr/bin/env python3
"""
Environment setup script for AI Chef Assistant.
Creates a .env file template for configuration.
"""

import os

def create_env_template():
    """Create a .env template file"""
    env_content = """# AI Chef Assistant Environment Variables
# Replace with your actual API key and endpoint

# GPT Endpoint for the AI model
GPT_ENDPOINT=https://api.openai.com/v1

# API Key (replace with your actual key)
OPENAI_API_KEY=your_api_key_here

# Alternative: If using a different provider, you can override the endpoint
# GPT_ENDPOINT=https://your-custom-endpoint.com/v1
"""
    
    env_path = ".env"
    
    if os.path.exists(env_path):
        print(f"⚠️  {env_path} already exists. Skipping creation.")
        return False
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Created {env_path} template")
        print("📝 Please edit .env and add your actual API key")
        return True
    except Exception as e:
        print(f"❌ Error creating {env_path}: {e}")
        return False

if __name__ == "__main__":
    create_env_template()
