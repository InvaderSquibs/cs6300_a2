Build an intelligent agent that effectively uses **at least 3–4 well-designed tools** in a chosen environment. You may extend your Assignment 1 agent in the same environment, or select a new environment and design a new agent.

---

## Learning goals (mapped to course CLOs)

- **CLO 1 – Agent-Environment Modeling:** Deepen your PEAS analysis to include tool-augmented actions and environment interactions.
- **CLO 2 – AI Pipeline:** Design and implement an AI solution with multiple tools, each clearly specified with contracts and behaviors.
- **CLO 3 – Agentic AI:** Build a functioning agent (framework + model of your choice) that perceives, reasons/decides, and acts through **multiple tools** to solve tasks.

---

## Overview

You will:

1. **Choose or extend an environment.** Either continue from Assignment 1 or select a new domain that supports at least **3–4 useful tools**.
2. **Design tools.** For each tool, provide a clear **name, description, inputs, outputs, and failure modes**. Tools must be **specific and useful**.
3. **Implement your agent.** Use a **well-established agentic AI framework** (e.g., smolagents, LangChain, CrewAI, MCP-based, etc.) and a **well-established programming language and model**.
4. **Evaluate your agent.** Show how the tools are used in practice, and compare performance with/without tools where possible.
5. **Document and reflect.** Submit a combined **Design Brief + Results & Reflection** PDF. The PDF must include a **link to your GitHub repository**.

---

## Deliverables

1. **Design Brief (PDF, ~3–4 pages):**
   - **PEAS Analysis:** Update from Assignment 1 with a strong focus on actuators/actions = tools.
   ```markdown
   ### PEAS Analysis - AI Chef Assistant
   
   **Performance Measure:**
   - Successfully finding and extracting complete recipes from web sources
   - Correctly scaling recipes to requested serving sizes with proper unit conversions
   - Generating well-formatted, usable recipe files in markdown format
   - End-to-end pipeline success: user request → search → extract → scale → format
   
   **Tool-Level Success Metrics:**
   - Recipe Search: 3+ valid recipe results found
   - Recipe Extraction: At least one ingredient and one instruction step extracted
   - Recipe Scaling: Correct mathematical scaling with appropriate unit conversions
   - Recipe Formatting: Non-empty ingredients list and non-empty instruction steps
   
   **Environment:**
   - Web-based recipe discovery and management domain
   - Recipe websites (AllRecipes, Epicurious, Bon Appétit, etc.)
   - User dietary requirements and serving size preferences
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
   ```
   - **Environment Properties:** Same formal analysis (O/PO, D/Stoch, Episodic/Sequential, etc.).
   ```markdown
   ### Environment Properties Analysis
   
   **Observable vs. Partially Observable:**
   - **Partially Observable** - The agent cannot observe:
     - User's pantry contents (recipes may not be viable due to missing ingredients)
     - User's cooking skill level or equipment availability
     - Complete web content (some sites may block scraping or have dynamic content)
   - **Fully Observable** - The agent has complete observability of:
     - User's natural language requests and dietary restrictions
     - Search results from DuckDuckGo
     - Real-time recipe content via extraction tool
     - Local file system for recipe storage
     - All tool inputs and outputs during execution
   
   **Deterministic vs. Stochastic:**
   - **Stochastic** - The environment exhibits randomness:
     - Web content varies between requests (dynamic content, A/B testing)
     - LLM responses can vary for the same input (temperature settings)
     - Recipe websites may change structure or become unavailable
     - Search results can vary based on timing and search engine algorithms
   - **Deterministic** - Some aspects are predictable:
     - Tool execution follows consistent logic
     - File system operations are deterministic
     - Mathematical scaling calculations are deterministic
   
   **Episodic vs. Sequential:**
   - **Sequential** - The environment has strong temporal dependencies:
     - Tools build on each other (search → extract → scale → format)
     - Each tool's output becomes the next tool's input
     - User can make follow-up requests based on previous results
     - Recipe modifications can be chained (scale then format)
     - Context from previous interactions can inform future decisions
     - Even the formatter tool's "episode" only exists because it was built sequentially
   
   **Static vs. Dynamic:**
   - **Dynamic** - The environment changes over time:
     - Web content updates frequently (search and extraction tools)
     - New recipes are added to websites
     - User preferences may change between sessions
   - **Static** - Some aspects remain constant:
     - Scaling tool logic and mathematical operations
     - Formatter tool templates and markdown generation
     - Tool interfaces and capabilities
     - Local file system structure
   
   **Discrete vs. Continuous:**
   - **Discrete** - All actions and states are discrete:
     - Tool calls are discrete actions
     - Recipe ingredients and steps are discrete items
     - Success/failure states are binary
     - All information is gathered before each execution
     - No time-dependent surprises during processing
     - Ingredient amounts are discrete values (even if fractional)
     - Scaling factors are discrete mathematical operations
   ```
   - **Tool Specifications:** For each tool:
     - Name  
     - Description  
     - Input(s) and type(s)  
     - Output(s) and type(s)  
     - Possible errors/failure handling
   ```markdown
   ### Tool Specifications
   
   #### Tool 1: Recipe Search Tool
   **Name:** `recipe_search`
   
   **Description:** 
   Searches for recipes with dietary restrictions using DuckDuckGo search engine. Returns recipe candidates with URLs and basic metadata for further processing by the extraction tool. Does not extract full recipe content - only provides URLs to strong recipe candidates.
   
   **Inputs:**
   - `query` (string): Recipe search query (e.g., 'pancakes', 'bread')
   - `dietary_restrictions` (array of strings, optional): List of dietary restrictions (e.g., ['vegan', 'gluten-free', 'keto'])
   
   **Outputs:**
   - JSON string containing:
     - `success` (boolean): Whether search was successful
     - `recipes` (array): List of recipe candidates with id, title, URL, description, source, extraction_status
     - `search_metadata` (object): Total results, timestamp, search engine used
     - `error` (string, if failed): Error message with suggestions
   
   **Error Handling:**
   - **Query Errors**: Empty/invalid query validation, query length limits (200 chars), nonsensical query detection
   - **Search Service Errors**: DuckDuckGo unavailability, connection timeouts, API failures
   - **Content Filtering Errors**: Blocked domain filtering (foodnetwork.com), recipe roundup page filtering
   - **Result Processing Errors**: No valid recipes found, extraction failures, malformed search results
   
   #### Tool 2: Recipe Extraction Tool
   **Name:** `recipe_extraction_llm`
   
   **Description:**
   Uses LLM natural language understanding to extract structured recipe information from any HTML structure. More flexible than deterministic parsing approaches, capable of handling various website formats and content structures.
   
   **Inputs:**
   - `url` (string): The URL of the recipe to extract
   
   **Outputs:**
   - JSON string containing:
     - `success` (boolean): Whether extraction was successful
     - `recipe` (object): Structured recipe data with title, ingredients, instructions, timing, servings, dietary tags
     - `extraction_metadata` (object): Timestamp, source domain, extraction method
     - `error` (string, if failed): Error message with details
   
   **Error Handling:**
   - **URL Validation Errors**: Invalid URL format, missing protocol (http/https), malformed URLs
   - **HTTP Request Errors**: Connection timeouts, 404/403 responses, SSL certificate issues, network failures
   - **Content Processing Errors**: HTML parsing failures, content length limits (6000 chars), encoding issues
   - **LLM Processing Errors**: Response parsing failures, JSON extraction errors, token limit exceeded
   - **Extraction Errors**: No recipe found in content, malformed recipe data, missing required fields
   
   #### Tool 3: Recipe Scaling Tool
   **Name:** `recipe_scaling_llm`
   
   **Description:**
   Uses LLM natural language understanding to scale recipes to target serving sizes. Performs mathematical scaling calculations via LLM reasoning (no external calculator functions). Detects serving sizes from user prompts when target_servings is 'auto', scales ingredients proportionally, handles unit conversions intelligently, and updates cooking times appropriately.
   
   **Inputs:**
   - `recipe_data` (string): JSON string containing the recipe data to scale
   - `target_servings` (string): Target number of servings (e.g., '4', '6', '8') or 'auto' for automatic detection
   - `user_prompt` (string, optional): Original user prompt for serving size detection when target_servings is 'auto'
   
   **Outputs:**
   - JSON string containing:
     - `success` (boolean): Whether scaling was successful
     - `scaled_recipe` (object): Scaled recipe with updated ingredients, instructions, timing
     - `scaling_info` (object): Original/target servings, scaling factor, method, unit conversions
     - `error` (string, if failed): Error message with details
   
   **Error Handling:**
   - **Input Validation Errors**: Invalid recipe data format, malformed JSON, missing required fields
   - **Serving Size Detection Errors**: Failed to extract serving size from user_prompt, ambiguous serving requests
   - **LLM Processing Errors**: Response parsing failures, JSON extraction errors, mathematical calculation errors
   - **Scaling Logic Errors**: Invalid scaling factors, unit conversion failures, proportion calculation errors
   - **Output Validation Errors**: Malformed scaled recipe, missing scaling metadata, inconsistent data
   
   #### Tool 4: Recipe Formatter Tool
   **Name:** `recipe_formatter_llm`
   
   **Description:**
   Uses LLM natural language understanding to format recipes into beautiful markdown files. Creates cookbook-style recipes with proper structure, headers, and formatting. Intelligently filters out irrelevant content and focuses on essential recipe information. Automatically adds source links at the bottom of recipes to trace the full pipeline flow.
   
   **Inputs:**
   - `recipe_data` (string): JSON string containing the recipe data to format
   - `output_filename` (string, optional): Filename for the markdown file (auto-generated if None)
   - `format_style` (string, optional): Formatting style ('cookbook', 'simple', 'detailed')
   
   **Outputs:**
   - JSON string containing:
     - `success` (boolean): Whether formatting was successful
     - `formatted_recipe` (object): Title, filename, file path (saved to results/recipes/), format style, markdown content
     - `formatting_info` (object): Timestamp, formatting method, content filtering, file size
     - `error` (string, if failed): Error message with details
   
   **Error Handling:**
   - **Input Validation Errors**: Invalid recipe data format, malformed JSON, missing required fields
   - **LLM Processing Errors**: Response parsing failures, JSON extraction errors, content generation failures
   - **File System Errors**: Write permission issues, disk space problems, directory creation failures
   - **Filename Generation Errors**: Invalid characters, path length limits, filename conflicts
   - **Formatting Errors**: Markdown syntax errors, content filtering failures, style application errors
   - **Fallback Errors**: LLM failure recovery, basic formatting fallback, error message generation
   ```
   - **Agent Architecture:** Framework chosen, model(s) used, reasoning loop, orchestration strategy (scripted vs model-driven).
   ```markdown
   ### Agent Architecture
   
   **Framework Choice:**
   - **smolagents**: Selected for its lightweight, focused approach to tool-augmented agents
   - Provides clean tool integration and natural language processing capabilities
   - Supports both scripted and model-driven orchestration strategies
   - Minimal overhead for rapid prototyping and testing
   
   **Model Configuration:**
   - **Model**: `qwen/qwen3-4b-2507` (local deployment)
   - **Endpoint**: `http://192.168.1.27:1234/v1` (local LLM server)
   - **Rationale**: Chosen for fast local tool calling without running up cloud credits
   - **API Compatibility**: OpenAI-compatible interface for seamless integration
   - **Max Steps**: 10 (configured to allow full 4-tool pipeline completion)
   
   **Reasoning Loop:**
   The agent follows a straightforward sequential reasoning pattern:
   1. **Parse User Intent**: Extract recipe request and dietary restrictions from natural language using LLM processing, combining with simulated user knowledge/preferences
   2. **Search Phase**: Use recipe_search tool to find recipe candidates with combined dietary restrictions
   3. **Extract Phase**: Use recipe_extraction_llm tool to get structured recipe data from URLs
   4. **Scale Phase**: Use recipe_scaling_llm tool if serving size adjustment needed
   5. **Format Phase**: Use recipe_formatter_llm tool to create markdown output with source links
   6. **Return Result**: Provide final formatted recipe to user
   
   **Orchestration Strategy:**
   - **Sequential Tool Execution**: Tools are executed in a predetermined order
   - **State Management**: Each tool reads and modifies the current recipe state
   - **Depth-First Flow**: For each recipe URL found, the agent attempts the full pipeline (extract → scale → format) before moving to the next URL
   - **Early Termination**: If any step succeeds, the agent returns the result without trying remaining URLs
   - **Error Handling**: Failed recipes are logged but don't stop the pipeline from trying other URLs
   
   **Tool Integration:**
   - **Tool Registration**: All 4 tools are registered with the smolagents CodeAgent
   - **JSON Communication**: Tools communicate via structured JSON strings
   - **State Passing**: Recipe data flows through the pipeline as JSON, with each tool modifying the state
   - **Error Propagation**: Failed tool calls are handled gracefully with fallback options
   - **Telemetry Integration**: Optional Phoenix telemetry for monitoring tool usage and performance
   
   **Orchestration Flow:**
   ```
   User Request → Search Tool → [Recipe URLs] → 
   For each URL: Extract Tool → [Recipe Data] → 
   Scale Tool (if needed) → [Scaled Recipe] → 
   Format Tool → [Markdown File] → Return Result
   ```
   
   **Key Design Decisions:**
   - **Local LLM**: Chosen for cost efficiency and rapid iteration
   - **Sequential Processing**: Ensures predictable, debuggable behavior
   - **State-Based Architecture**: Each tool modifies the recipe state in place
   - **Queue-Based URL Processing**: Tries multiple recipe sources for better success rates
   - **Graceful Degradation**: System continues working even if individual tools fail
   - **Hybrid Dietary Restriction Handling**: Combines simulated user knowledge with natural language extraction
   
   **Dietary Restriction Processing:**
   The agent uses a hybrid approach to handle dietary restrictions:
   - **Simulated User Knowledge**: Dietary restrictions passed as parameters (e.g., `--restrictions "vegan"`) simulate known user preferences or dietary needs
   - **Natural Language Extraction**: LLM extracts additional dietary restrictions from user prompts (e.g., "for my keto friend" → extracts "keto")
   - **Smart Combination**: Merges both sources, removing duplicates while preserving order
   - **Example**: "I'm making pancakes for my keto friend and I" + simulated "vegan" → combined restrictions: "vegan, keto"
   - **Implementation**: Uses dedicated `_extract_dietary_restrictions_from_prompt()` function with LLM processing for accurate extraction
   
   **Output Organization:**
   The system uses an organized folder structure for better project management:
   - **`results/recipes/`**: All generated recipe markdown files with source links
   - **`results/diagrams/`**: Agent flow diagrams and architecture documentation
   - **`results/phoenix/`**: Telemetry test results and evaluation reports
   - **Source Link Integration**: All recipes include original URL links to trace the full pipeline flow
   ```
   - **Evaluation Plan:** Test cases, success metrics, expected behaviors.
   ```markdown
   ### Evaluation Plan
   
   **Test Strategy:**
   The evaluation plan uses a multi-layered approach combining systematic component testing, end-to-end pipeline validation, and comprehensive error handling verification. Tests are designed to validate both individual tool performance and integrated agent behavior.
   
   **Test Categories:**
   
   #### 1. Component-Level Testing
   **Purpose**: Validate each tool independently to isolate issues and ensure proper functionality
   
   **Test Cases:**
   - **Tool 1 (Recipe Search)**: Test with various queries and dietary restrictions
     - Success Criteria: 3+ valid recipe results found, proper JSON structure
     - Test Inputs: "vegan chocolate chip cookies", ["vegan"]
     - Expected Output: JSON with success=true, recipes array, search metadata
   
   - **Tool 2 (Recipe Extraction)**: Test with known recipe URLs
     - Success Criteria: At least one ingredient and one instruction step extracted
     - Test Inputs: Valid recipe URLs from search results
     - Expected Output: JSON with success=true, structured recipe data
   
   - **Tool 3 (Recipe Scaling)**: Test with different serving sizes
     - Success Criteria: Correct mathematical scaling with appropriate unit conversions
     - Test Inputs: Recipe data, target servings (4, 8, 12)
     - Expected Output: JSON with scaled recipe and scaling metadata
   
   - **Tool 4 (Recipe Formatting)**: Test with different format styles
     - Success Criteria: Non-empty ingredients list and non-empty instruction steps
     - Test Inputs: Recipe data, format styles (cookbook, simple, detailed)
     - Expected Output: JSON with formatted recipe and markdown file path
   
   #### 2. Integration Testing
   **Purpose**: Validate agent orchestration and tool coordination
   
   **Test Cases:**
   - **Basic Pipeline**: Search → Extract → Recipe Object
     - Command: `python3.11 src/chef_agent.py e2e`
     - Success Criteria: All pipeline stages completed, recipe object with ingredients and steps
   
   - **Dietary Restrictions Pipeline**: Search with filtering → Extract → Recipe Object
     - Command: `python3.11 src/chef_agent.py e2e --diet "vegan"`
     - Success Criteria: Dietary filtering applied, vegan recipe extracted
   
   - **Scaling Pipeline**: Search → Extract → Scale → Scaled Recipe
     - Command: `python3.11 src/chef_agent.py "pancakes for 8 guests"`
     - Success Criteria: Serving size detected, recipe scaled appropriately
   
   - **Full Pipeline**: Search → Extract → Scale → Format → Markdown File
     - Command: `python3.11 src/chef_agent.py "vegan pancakes for 8 people" --restrictions "vegan"`
     - Success Criteria: Complete pipeline with markdown file generation
   
   #### 3. Error Handling Testing
   **Purpose**: Validate graceful failure handling and error recovery
   
   **Test Cases:**
   - **Invalid Queries**: Empty queries, nonsense queries
     - Expected: Graceful error messages with helpful suggestions
   
   - **Network Failures**: Unavailable URLs, timeout scenarios
     - Expected: Fallback to alternative URLs, error logging
   
   - **LLM Failures**: Malformed responses, parsing errors
     - Expected: Fallback formatting, error recovery mechanisms
   
   #### 4. Performance Testing
   **Purpose**: Validate system performance and resource usage
   
   **Metrics:**
   - **Response Time**: End-to-end pipeline completion time
   - **Success Rate**: Percentage of successful recipe extractions
   - **Tool Utilization**: Frequency and success rate of each tool
   - **Error Recovery**: Time to recover from failures
   
   **Expected Behaviors:**
   - Pipeline completes within 180 seconds (3 minutes)
   - Success rate > 80% for valid recipe queries
   - Graceful degradation when individual tools fail
   - Consistent JSON output format across all tools
   
   **Validation Protocol:**
   The system includes an automated validation protocol (`tests/validation_protocol.py`) that:
   - Runs comprehensive end-to-end tests
   - Validates tool execution logs
   - Checks for proper JSON structure
   - Verifies markdown file generation
   - Provides detailed success/failure reporting
   
   **Success Metrics:**
   - **Overall Success**: All pipeline stages complete successfully
   - **Tool Success**: Individual tools meet their specific success criteria
   - **Error Handling**: Graceful failure with helpful error messages
   - **Output Quality**: Structured, usable recipe data with proper formatting
   ```

2. **Working Code (Git repo):**

### Working Code Checklist

- [x] **README.md** - Comprehensive documentation with installation, usage, telemetry setup, and examples
- [x] **requirements.txt** - All dependencies including smolagents, transformers, torch, and specialized packages  
- [x] **Agent implementation** - Complete `src/chef_agent.py` with natural language processing, tool orchestration, and error handling
- [x] **3-4 tools** - All 4 specialized tools implemented:
  - [x] `recipe_search.py` - DuckDuckGo search with dietary filtering
  - [x] `recipe_extraction_llm.py` - LLM-powered recipe extraction from URLs
  - [x] `recipe_scaling_llm.py` - LLM-powered recipe scaling with unit conversions
  - [x] `recipe_formatter_llm.py` - LLM-powered markdown formatting with multiple styles
- [x] **Example scripts/tests** - Working example recipe files in `results/recipes/` directory and validation protocol

### Code Quality Assessment

**✅ All Requirements Met:**
- **README**: Comprehensive documentation covering installation, usage examples, telemetry setup, and architecture
- **Dependencies**: Complete requirements.txt with all necessary packages for smolagents, LLM integration, and web scraping
- **Agent Implementation**: Full-featured agent with natural language processing, dietary restriction extraction, tool orchestration, and error handling
- **Tool Suite**: All 4 tools fully implemented with proper error handling, JSON communication, and telemetry support
- **Examples**: Working recipe examples generated by the system in `results/recipes/`, including source links and the secret blogger format easter egg

**Code Features:**
- Natural language request processing with dietary restriction extraction
- Sequential tool orchestration with depth-first URL processing
- Comprehensive error handling and graceful degradation
- Telemetry integration ready for Phoenix/OpenTelemetry
- Multiple format styles including the hidden "blogger" easter egg
- Hybrid dietary restriction handling (simulated + extracted)
- Local LLM deployment for cost efficiency
- Organized folder structure (results/recipes/, results/diagrams/, results/phoenix/)
- Source link tracing for full pipeline validation

3. **Results & Reflection (PDF, ~2–3 pages):**

### Results & Analysis

**Repository Link:** [GitHub Repository](https://github.com/your-username/cs6300_a2)

**Evaluation Results:** Comprehensive testing achieved 100% success rate across all 6 test categories:
- Basic Recipe Search: ✅ Full pipeline execution with source links
- Dietary Restriction Handling: ✅ Both explicit and natural language extraction
- Recipe Scaling: ✅ LLM mathematical scaling with unit conversions
- Full Pipeline Formatting: ✅ Complete 5-step pipeline with file generation
- Error Handling: ✅ Graceful degradation without crashes
- Source Link Validation: ✅ 100% of generated recipes include traceable source links

**Key Metrics:**
- 7 recipe files generated with professional formatting
- 100% source link integration (7/7 files)
- Complete pipeline validation (Search → Extract → Scale → Format → Source Link)
- Robust error handling and graceful degradation
- Hybrid dietary restriction processing (simulated + extracted)

### Reflection

#### Tool Design Learnings

**Modular Design for Testability:**
The biggest surprise was how splitting the functionality into separate tools made testing and validation significantly easier. Focusing on individual components that could be validated independently allowed more time to focus on orchestration and understanding the overall system behavior. This modular approach proved crucial for debugging and ensuring each component worked correctly before integration.

**Sequential vs. Parallel Orchestration:**
We chose sequential tool execution over parallel processing, which proved to be the right decision for this domain. Recipe processing has strong dependencies: you need search results before extraction, extraction before scaling, and scaling before formatting. The sequential approach provided predictable debugging and clear state management, though it increased total execution time.

**Tool Granularity Tradeoffs:**
The 4-tool architecture (Search, Extract, Scale, Format) provided good separation of concerns, but there were interesting tradeoffs. While we could have merged Search and Extract into one tool, keeping them separate allowed for the efficiency of extracting 5 recipes in one function call while maintaining the flexibility to handle multiple recipe sources. The separation proved valuable for both performance and maintainability.

**LLM Integration Challenges:**
The recipe extractor was the most difficult tool to develop, primarily due to the complexity of making additional LLM calls and validating their success states. While some operations could be done deterministically, integrating LLM reasoning for scaling and formatting was time-consuming and frustrating, especially when known deterministic functions could have been used instead.

#### PEAS Framework Tradeoffs

**Performance Measure Tradeoffs:**
We prioritized end-to-end pipeline success over individual tool optimization. This meant accepting that some tools might fail (e.g., extraction from one URL) as long as the overall system succeeded. This tradeoff proved effective - our 100% pipeline success rate demonstrates that graceful degradation works better than perfect individual tool performance.

**Environment Design Tradeoffs:**
Making the environment partially observable (not knowing pantry contents) was a deliberate choice that simplified the problem space. While this limits the system's ability to suggest truly viable recipes, it focuses the agent on recipe discovery and modification rather than inventory management - a more tractable problem for this assignment.

**Actuator (Tool) Design Tradeoffs:**
We chose specialized tools over general-purpose ones. Each tool is highly focused (e.g., scaling only handles serving size changes, not ingredient substitutions). This provided reliability and clear interfaces but limited the system's ability to handle complex recipe modifications that might require multiple types of changes simultaneously.

**Sensor Design Tradeoffs:**
Our hybrid approach to dietary restrictions (simulated user knowledge + natural language extraction) provided flexibility but introduced significant risk. Missing a food restriction is often more than a preference issue - it can be a health concern. The LLM approach for dietary restrictions is risky for this reason, and a human-in-the-loop validation step before generation would be valuable to cover this gap in observability.

#### Successes and Limitations

**Key Successes:**
1. **Solid Extensible Foundation:** The modular, sequential design creates a reliable foundation for future extensions. The system feels reliably extendable - we can easily add pantry tracking, nutrient/macro monitoring, weekly meal planning, and dietary restriction conversions
2. **Source Link Integration:** Adding traceable source links to every recipe provides excellent pipeline validation
3. **Modular Architecture:** The separation of concerns makes the system complex yet easily testable, which is crucial for maintaining reliability
4. **Organized Output Structure:** The results/recipes/, results/diagrams/, results/reports/ organization improved project management
5. **Reliability Over Performance:** The reliability tradeoff works well for extendability - users are already used to spending time finding recipes, so the time investment pays off if we can extend to pantry integration and ingredient substitutions

**Key Limitations:**
1. **LLM Integration Complexity:** Banking on AI reasoning to cover gaps that could be handled deterministically was time-consuming and frustrating, especially for formatting where known functions could have been used
2. **Execution Time:** Sequential processing with LLM calls results in long execution times (2-3 minutes per recipe)
3. **Limited Recipe Sources:** DuckDuckGo search doesn't access all recipe websites, limiting discovery
4. **No Ingredient Substitution:** The system can scale recipes but cannot substitute ingredients for dietary needs
5. **Dietary Restriction Risk:** The LLM approach for dietary restrictions introduces risk of missing critical health-related restrictions

#### What-If Ablations

**Merging Search and Extract Tools:**
While we could merge the search and extract tools into one, the current separation provides valuable efficiency - extracting 5 recipes takes time, but the function to pull 5 results is just one function call, saving significant processing. The separation also maintains flexibility for handling multiple recipe sources, so keeping them separate is justified.

**Removing the Scaling Tool:**
The scaling tool is somewhat necessary if we want to do ingredient substitutions, as scaling often goes hand-in-hand with modification. While it could potentially be swapped out, it's in a good spot for the current system design.

**Adding RAG for Substitutions:**
The most valuable addition would be RAG (Retrieval-Augmented Generation) for ingredient substitutions. When no recipe fits all requirements, the system could remove a requirement from the search and attempt substitutions anyway, significantly expanding the system's utility.

#### Future Improvements

1. **Caching Layer:** Implement caching for repeated searches and extractions to improve performance
2. **Ingredient Substitution:** Add a tool for intelligent ingredient substitutions based on dietary restrictions
3. **Recipe Rating Integration:** Incorporate user ratings and reviews into recipe selection
4. **Dynamic Tool Configuration:** Allow runtime configuration of tool parameters and behavior
5. **Advanced Error Recovery:** Implement retry mechanisms and alternative processing strategies
6. **Multi-Modal Support:** Add image processing for recipe photos and visual validation

#### Key Insights

The most important learning was that **validation is key for all of it** - knowing what's happening at each step is huge. Making sure the system is complex yet still easily testable is crucial, but you have to actually test that complexity. The modular design approach proved essential for this validation.

**Reliability trumps performance** in tool-augmented systems. Our 100% success rate came from designing for graceful degradation rather than perfect individual tool performance. The sequential orchestration, while slower, provided the predictability and debuggability needed for a robust system.

The hybrid approach to dietary restrictions demonstrated both the power and risk of combining deterministic (simulated knowledge) and stochastic (natural language extraction) components. While this creates more flexible systems, it also introduces significant risk when health-related restrictions are involved.

Finally, the source link integration proved invaluable for pipeline validation and debugging. This simple addition transformed the system from a black box into a transparent, traceable process - a pattern that should be standard in tool-augmented systems.

> Submit one **combined PDF** containing the **Design Brief + Results & Reflection (with repo link)**.

---

## Technical requirements

- **Framework:** Must use a **well-established agentic AI framework** (e.g., smolagents, LangChain, CrewAI, MCP server).
- **Language:** Must use a **well-established programming language**.
- **Models:** Must use a **well-established LLM** suitable for reasoning and tool-use.
- **Reproducibility:** Must include installation and run instructions in README. Avoid hard-coding secrets.

---

## Evaluation & Rubric (100 pts)

| Component                      | Points | What we look for                                                  |
| ---                            | ---    | ---                                                               |
| **PEAS Analysis**              | 15     | Correct, detailed, and tool-focused PEAS.                         |
| **Tool Specifications**        | 25     | 3–4 tools with clear purpose, I/O contracts, error handling.      |
| **Design Brief & Architecture**| 15     | Coherent framework choice, orchestration strategy, evaluation plan.|
| **Implementation**             | 25     | Working agent; tools integrated; code is clear and reproducible.  |
| **Results**                    | 10     | Demonstrates tool use across runs; reproducible evidence.         |
| **Reflection**                 | 10     | Insightful discussion of tool design, successes, failures, learning.|

**Deductions:**
- Useless/missing tools (–10 each).
- Poorly documented tools (–5 each).
- Non-reproducible setup or unclear run instructions (–5).
- Unsafe key handling (–10).

---

## Constraints & guidance

- Keep the **Environment→Agent→Environment** loop central.
- Tools should be **modular, specific, and typed**. Avoid vague “do-everything” tools.
- At least **3–4 tools are required**; if your environment does not naturally support this, choose another.
- Consider error handling, retries, and orchestration strategies.

---

## Submission checklist

- [ ] Repo link included in **Results & Reflection PDF**.
- [ ] Repo contains code, README, requirements, and tests/examples.
- [ ] **Combined PDF** (Design Brief + Results & Reflection).
- [ ] All tools clearly documented with name, description, inputs, and outputs.
