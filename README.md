# AI Chef Assistant

A multi-tooled AI agent that helps with recipe curation, scaling, and formatting using the smolagents framework. The assistant can search for recipes with dietary restrictions, extract detailed recipe information, scale recipes for different serving sizes, and format them into beautiful markdown files.

## Features

- **🔍 Recipe Search**: Find recipes with dietary restrictions using DuckDuckGo search
- **📄 Recipe Extraction**: Extract detailed recipe information from any website using LLM natural language understanding
- **⚖️ Recipe Scaling**: Intelligently scale recipes for different serving sizes with unit conversions
- **📝 Recipe Formatting**: Generate beautiful markdown recipe files in cookbook style

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install smolagents duckduckgo-search requests beautifulsoup4 openai python-dotenv
   ```
3. Set up your environment variables in `.env`:
   ```
   GPT_ENDPOINT=http://192.168.1.27:1234/v1
   MODEL_ID=qwen/qwen3-4b-2507
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

### Natural Language Requests (Recommended)

```bash
# Basic recipe request
python3.11 src/chef_agent.py "I'd like some pancakes please"

# With dietary restrictions
python3.11 src/chef_agent.py "I'd like some pancakes please" --restrictions vegan,gluten-free

# With scaling for specific serving size
python3.11 src/chef_agent.py "I'd like some vegan pancakes for a family gathering with 12 people" --restrictions vegan
```

### Legacy Commands

```bash
# Show help and available tools
python3.11 src/chef_agent.py help

# Search for recipes
python3.11 src/chef_agent.py search "pancakes"
python3.11 src/chef_agent.py search "pancakes" --diet "vegan,gluten-free"

# Extract recipe from URL
python3.11 src/chef_agent.py extract "https://www.allrecipes.com/recipe/191885/vegan-pancakes/"

# Run end-to-end tests
python3.11 src/chef_agent.py e2e
python3.11 src/chef_agent.py e2e --diet "vegan"

# Interactive mode
python3.11 src/chef_agent.py
```

## Output

The AI Chef Assistant generates beautiful markdown recipe files in the `results/` directory. Each recipe includes:

- **Professional formatting** with clear sections and headers
- **Complete ingredient lists** with proper measurements
- **Step-by-step instructions** with cooking tips
- **Timing information** (prep time, cook time, total time)
- **Dietary information** and source attribution
- **Enhanced descriptions** and helpful cooking notes

### Example Output File

Recipes are saved as markdown files in the `results/` directory, for example:
- `results/vegan_pancakes.md`
- `results/chocolate_chip_cookies.md`
- `results/gluten_free_bread.md`

## Supported Dietary Restrictions

- vegan, vegetarian
- keto, paleo
- gluten-free, dairy-free
- nut-free, soy-free
- sugar-free, low-carb, high-protein

## Architecture

The AI Chef Assistant uses a **LLM-first approach** with 4 specialized tools:

1. **RecipeSearchTool**: Searches for recipes with dietary filtering
2. **RecipeExtractionLLMTool**: Extracts recipe data using LLM natural language understanding
3. **RecipeScalingLLMTool**: Scales recipes intelligently with unit conversions
4. **RecipeFormatterLLMTool**: Formats recipes into beautiful markdown files

## Testing

Run the validation protocol to test all functionality:

```bash
# Fast mode (basic test)
python3.11 tests/validation_protocol.py --fast

# Full validation suite
python3.11 tests/validation_protocol.py
```

## Development

The project follows a modular architecture with separate tool files:

- `src/chef_agent.py` - Main agent orchestrator
- `src/tools/recipe_search.py` - Recipe search functionality
- `src/tools/recipe_extraction_llm.py` - LLM-powered recipe extraction
- `src/tools/recipe_scaling_llm.py` - LLM-powered recipe scaling
- `src/tools/recipe_formatter_llm.py` - LLM-powered recipe formatting
- `tests/validation_protocol.py` - Comprehensive test suite

## License

This project is part of the cs6300 course work and demonstrates advanced AI agent development using the smolagents framework.