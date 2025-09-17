# AI Chef Assistant

A multi-tooled AI agent that helps with recipe curation, scaling, and formatting using the smolagents framework. The assistant can search for recipes with dietary restrictions, extract detailed recipe information, scale recipes for different serving sizes, and format them into beautiful markdown files.

## Features

- **🔍 Recipe Search**: Find recipes with dietary restrictions using DuckDuckGo search with detailed URL listings
- **📄 Recipe Extraction**: Extract detailed recipe information from any website using LLM natural language understanding with ingredient/step counts
- **⚖️ Recipe Scaling**: Intelligently scale recipes for different serving sizes with unit conversions and scaling factor validation
- **📝 Recipe Formatting**: Generate beautiful markdown recipe files in cookbook style with file size and formatting details
- **🔍 Enhanced Logging**: Detailed tool deliverables showing URLs found, ingredient counts, scaling math, and file generation
- **📊 Telemetry Ready**: Built for easy integration with Phoenix, Opik, or LangWatch for advanced monitoring

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

# Example with detailed tool deliverables
python3.11 src/chef_agent.py "I'd like to make chocolate chip cookies for 8 people" --restrictions "vegan"
```

### Enhanced Output

The assistant now provides detailed deliverables from each tool:

- **🔗 Search Tool**: Shows all URLs found with titles and descriptions
- **📋 Extraction Tool**: Displays ingredient count, step count, timing, and dietary tags
- **📊 Scaling Tool**: Shows original→target servings, scaling factor, and unit conversions
- **📄 Formatter Tool**: Displays filename, file path, file size, and formatting method

## Telemetry & Monitoring

The AI Chef Assistant is built with OpenTelemetry support for advanced monitoring and debugging:

### Phoenix Integration (Recommended)

**1. Install Dependencies:**
```bash
pip install 'smolagents[telemetry]' opentelemetry-sdk opentelemetry-exporter-otlp openinference-instrumentation-smolagents
```

**2. Start Phoenix Server:**
```bash
python -m phoenix.server.main serve
```
Phoenix will be available at: http://localhost:6006

**3. Enable Telemetry:**
```bash
# Option 1: Environment variable
export ENABLE_TELEMETRY=true
python3.11 src/chef_agent.py "I'd like some pancakes"

# Option 2: Direct import
python3.11 -c "from src.telemetry_config import enable_telemetry; enable_telemetry(); import src.chef_agent"
```

**4. View Metrics:**
Open http://localhost:6006 in your browser to see:

#### **📊 Tracked Metrics:**

**🔍 Search Tool Metrics:**
- `search.query`: Search query used
- `search.results_count`: Number of recipes found
- `search.dietary_restrictions`: Applied dietary filters
- `search.filtered_count`: Recipes after filtering
- `search.success_rate`: Search success percentage

**📄 Extraction Tool Metrics:**
- `extraction.url`: Recipe URL being extracted
- `extraction.ingredients_count`: Number of ingredients found
- `extraction.instructions_count`: Number of instruction steps
- `extraction.servings`: Recipe serving size
- `extraction.prep_time`: Preparation time
- `extraction.cook_time`: Cooking time
- `extraction.dietary_tags`: Detected dietary tags
- `extraction.success_rate`: Extraction success percentage

**⚖️ Scaling Tool Metrics:**
- `scaling.original_servings`: Original recipe servings
- `scaling.target_servings`: Target servings requested
- `scaling.scaling_factor`: Mathematical scaling factor (e.g., 2.0 for 4→8)
- `scaling.scaling_method`: Method used (proportional, time_adjusted)
- `scaling.unit_conversions_count`: Number of unit conversions performed
- `scaling.success_rate`: Scaling success percentage

**📝 Formatter Tool Metrics:**
- `formatter.recipe_title`: Recipe title being formatted
- `formatter.filename`: Generated markdown filename
- `formatter.file_size`: Size of generated markdown file
- `formatter.format_style`: Formatting style used
- `formatter.content_filtering`: Content filtering applied
- `formatter.success_rate`: Formatting success percentage

**🔄 Pipeline Metrics:**
- `pipeline.total_duration`: End-to-end execution time
- `pipeline.tool_sequence`: Order of tool execution
- `pipeline.success_rate`: Overall pipeline success rate
- `pipeline.error_types`: Types of errors encountered

### Alternative Platforms
- **Opik**: Built-in OpenTelemetry support with Comet integration
- **LangWatch**: Automatic tracing with dashboard visualization

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

The AI Chef Assistant generates beautiful markdown recipe files in the `results/recipes/` directory. Each recipe includes:

- **Professional formatting** with clear sections and headers
- **Complete ingredient lists** with proper measurements
- **Step-by-step instructions** with cooking tips
- **Timing information** (prep time, cook time, total time)
- **Dietary information** and source attribution
- **Enhanced descriptions** and helpful cooking notes

### Example Output File

Recipes are saved as markdown files in the `results/recipes/` directory, for example:
- `results/recipes/vegan_pancakes.md`
- `results/recipes/chocolate_chip_cookies.md`
- `results/recipes/gluten_free_bread.md`

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