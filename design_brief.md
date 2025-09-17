# AI Chef Assistant - Design Brief

**CS6300 - Assignment 2: Tool-Augmented Agents**  
**Student:** Zachary Walton  
**Date:** September 17, 2025

---

## PEAS Analysis

**Performance Measure:**
- End-to-end pipeline success: user request → search → extract → scale → format
- Successfully finding and extracting complete recipes from web sources
- Correctly scaling recipes to requested serving sizes with proper unit conversions
- Generating well-formatted, usable recipe files in markdown format

**Environment:**
- Web-based recipe discovery and management domain
- Recipe search (Duck Duck Go)
- User dietary requirements 
- Secondary Dietary requirements and serving size preferences derived from prompt
- Local file system for recipe storage and output

**Actuators (Tools):**
1. **Recipe Search Tool** - Searches for recipes using DuckDuckGo with dietary filtering
2. **Recipe Extraction Tool** - Uses LLM to extract structured recipe data from URLs
3. **Recipe Scaling Tool** - Uses LLM to scale recipes to target serving sizes
4. **Recipe Formatter Tool** - Uses LLM to create beautiful markdown recipe files

**Sensors:**
- Web scraping capabilities for recipe content extraction
- Natural language processing for user input parsing
- LLM processing for content understanding and transformation
- File system access for reading/writing recipe files

## Environment Properties

**Observable vs. Partially Observable:**
- **Partially Observable** - Cannot observe user's pantry contents, cooking skill level, or complete web content
- **Fully Observable** - User requests, search results, recipe content, file system, tool inputs/outputs

**Deterministic vs. Stochastic:**
- **Stochastic** - Web content varies, LLM responses vary, search results vary
- **Deterministic** - Tool execution logic, file system operations, mathematical scaling

**Episodic vs. Sequential:**
- **Sequential** - Tools build on each other (search → extract → scale → format), strong temporal dependencies

**Static vs. Dynamic:**
- **Static** - Scaling logic, formatter templates, tool interfaces. All dynamic pieces will not change during evaluation (Web content updates frequently, new recipes added)

**Discrete vs. Continuous:**
- **Discrete** - All actions and states are discrete, no time-dependent surprises

## Tool Specifications

**Tool 1: Recipe Search Tool**
- Inputs: `query` (string), `dietary_restrictions` (array, optional)
- Outputs: JSON with success, recipes array, search metadata, error
- Error Handling: Query validation, search service errors, content filtering

**Tool 2: Recipe Extraction Tool**
- Inputs: `url` (string)
- Outputs: JSON with success, structured recipe data, extraction metadata, error
- Error Handling: URL validation, HTTP errors, content processing, LLM processing

**Tool 3: Recipe Scaling Tool**
- Inputs: `recipe_data` (string), `target_servings` (string), `user_prompt` (string, optional)
- Outputs: JSON with success, scaled recipe, scaling info, error
- Error Handling: Input validation, serving size detection, LLM processing

**Tool 4: Recipe Formatter Tool**
- Inputs: `recipe_data` (string), `output_filename` (string, optional), `format_style` (string, optional)
- Outputs: JSON with success, formatted recipe, formatting info, error
- Error Handling: Input validation, LLM processing, file system errors

*Detailed tool specifications are available in source code docstrings.*

## Agent Architecture

**Framework:** smolagents - lightweight, focused approach to tool-augmented agents

**Model Configuration:**
- **Model:** `qwen/qwen3-4b-2507` (local deployment)
- **Endpoint:** `http://192.168.1.27:1234/v1` (local LLM server)
- **Max Steps:** 10 (configured for full 4-tool pipeline completion)

**Reasoning Loop:**
1. Parse User Intent - Extract recipe request and dietary restrictions
2. Search Phase - Use recipe_search tool to find candidates
3. Extract Phase - Use recipe_extraction_llm tool to get structured data
4. Scale Phase - Use recipe_scaling_llm tool if serving size adjustment needed
5. Format Phase - Use recipe_formatter_llm tool to create markdown output
6. Return Result - Provide final formatted recipe to user

**Orchestration Strategy:**
- Sequential tool execution with predetermined order
- State management where each tool reads and modifies current recipe state
- Depth-first flow: attempt full pipeline for each URL before trying next
- Early termination if any step succeeds
- Graceful error handling with fallback options

**Key Design Decisions:**
- Local LLM for cost efficiency and rapid iteration
- Sequential processing for predictable, debuggable behavior
- State-based architecture with JSON communication
- Queue-based URL processing for better success rates
- Hybrid dietary restriction handling (simulated + natural language extraction)

## Evaluation Plan

**Test Strategy:** Multi-layered approach combining component testing, end-to-end validation, and error handling verification.

**Test Categories:**

1. **Component-Level Testing**
   - Tool 1: 3+ valid recipe results, proper JSON structure
   - Tool 2: At least one ingredient and instruction step extracted
   - Tool 3: Correct mathematical scaling with unit conversions
   - Tool 4: Non-empty ingredients list and instruction steps

2. **Integration Testing**
   - Basic Pipeline: Search → Extract → Recipe Object
   - Dietary Restrictions Pipeline: Search with filtering → Extract → Recipe Object
   - Scaling Pipeline: Search → Extract → Scale → Scaled Recipe
   - Full Pipeline: Search → Extract → Scale → Format → Markdown File

3. **Error Handling Testing**
   - Invalid queries, network failures, LLM failures
   - Expected: Graceful error messages, fallback mechanisms, error recovery

4. **Performance Testing**
   - Response time, success rate, tool utilization, error recovery
   - Expected: Pipeline completes within 180 seconds, success rate >80%, graceful degradation

**Success Metrics:**
- Overall Success: All pipeline stages complete successfully
- Tool Success: Individual tools meet specific success criteria
- Error Handling: Graceful failure with helpful error messages
- Output Quality: Structured, usable recipe data with proper formatting

---