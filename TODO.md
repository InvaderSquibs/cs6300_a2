# AI Chef Assistant - Development Checklist

## Project Overview
Building a multi-tooled AI chef assistant using smolagents framework with 3 specialized tools for recipe curation and modification.

## Tool Architecture
- **Tool 1**: Recipe Search & Extraction (with dietary filtering)
- **Tool 2**: Recipe Scaling & Unit Conversion (intelligent unit handling)
- **Tool 3**: Recipe Validation & Final Formatting (completeness & structure)

## Development Phases

### Phase 1: Foundation Setup
- [x] Set up basic smolagents framework with 'Hello AI' validation
- [x] Configure environment and dependencies
- [x] Establish basic agent structure
- [x] Create modular tool structure with separate files
- [x] Test tool connection and agent communication
- [x] Organize tests in dedicated test folder with tool-specific naming

### Phase 2: Tool 1 - Recipe Search Tool
- [x] Build Tool 1: Recipe Search Tool with dietary filtering
  - [x] Implement duckduckgo-search for recipe URLs
  - [x] Target recipe sites (AllRecipes, Food Network, etc.)
  - [x] Return clean JSON with recipe URLs and metadata
  - [x] Add comprehensive docstrings and documentation
- [x] Test Tool 1 with "vegan pancakes" search
- [x] Validate JSON output format for AI consumption
- [x] Test Tool 1 with various dietary restrictions and validate ≥3 recipes returned
- [x] Add error handling for no results scenarios
- [x] **FULL VALIDATION TEST**: Help docs → Tool invocation → JSON validation

### Phase 2.5: Tool 2 - Recipe Extraction Tool
- [ ] Build Tool 2: Recipe Extraction Tool
  - [ ] Implement web scraping with requests + BeautifulSoup
  - [ ] Parse recipe data (ingredients, instructions, servings, cook time)
  - [ ] Handle different recipe site formats (AllRecipes, Food Network, etc.)
  - [ ] Return structured recipe data in clean JSON format
  - [ ] Add comprehensive docstrings and documentation
- [ ] Test Tool 2 with AllRecipes URL
- [ ] Test Tool 2 with various recipe site formats
- [ ] Add error handling for extraction failures
- [ ] **FULL VALIDATION TEST**: Help docs → Tool invocation → JSON validation
- [ ] **CHAINING VALIDATION**: Tool 1 → Tool 2 pipeline test

### Phase 3: Tool 3 - Recipe Scaling & Unit Conversion
- [ ] Build Tool 3: Recipe Scaling & Unit Conversion with intelligent unit handling
  - [ ] Implement serving size scaling logic
  - [ ] Add unit conversion capabilities (tbsp→cups, etc.)
  - [ ] Handle fractional measurements and rounding
  - [ ] Return scaled recipe in clean JSON format
  - [ ] Add comprehensive docstrings and documentation
- [ ] Test Tool 3 with different serving sizes and unit conversions
- [ ] Validate scaling accuracy and unit conversion logic
- [ ] **FULL VALIDATION TEST**: Help docs → Tool invocation → JSON validation
- [ ] **CHAINING VALIDATION**: Tool 1 → Tool 2 → Tool 3 pipeline test

### Phase 4: Tool 4 - Recipe Validation & Final Formatting
- [ ] Build Tool 4: Recipe Validation & Final Formatting with completeness checks
  - [ ] Implement recipe completeness validation (ingredients + steps)
  - [ ] Add proper formatting and structure validation
  - [ ] Handle missing or incomplete recipe data
  - [ ] Return validated and formatted recipe in clean JSON format
  - [ ] Add comprehensive docstrings and documentation
- [ ] Test Tool 4 with incomplete recipes and validate proper formatting output
- [ ] Ensure clear section organization (ingredients, steps, etc.)
- [ ] **FULL VALIDATION TEST**: Help docs → Tool invocation → JSON validation
- [ ] **CHAINING VALIDATION**: Tool 1 → Tool 2 → Tool 3 → Tool 4 pipeline test

### Phase 5: Integration & Testing
- [ ] Full pipeline integration testing with error handling and fallback scenarios
- [ ] Test complete workflow: search → extract → scale → validate
- [ ] Implement fallback logic (try next recipe if current fails)
- [ ] Stress test with various edge cases
- [ ] **COMPREHENSIVE VALIDATION**: All tools + help system + chaining tests

## Validation Testing Protocol

### For Each Tool (Tool 1, 2, 3, 4):
1. **Help Documentation Test**
   ```bash
   python3.11 src/chef_agent.py help
   # Verify tool appears in AVAILABLE TOOLS section
   ```

2. **Individual Tool Test**
   ```bash
   python3.11 src/chef_agent.py search "test query"
   # Verify JSON output format and data quality
   # Note: Agent may format JSON as human-readable text
   ```

3. **Error Handling Test**
   ```bash
   python3.11 src/chef_agent.py search ""
   python3.11 src/chef_agent.py search "invalid_query_12345"
   # Verify graceful error handling
   ```

### For Chaining Validation (Tool 2+):
4. **Pipeline Test**
   ```bash
   # Test Tool 1 → Tool 2
   python3.11 src/chef_agent.py search "vegan pancakes"
   # Then test extraction with returned URL
   
   # Test Tool 1 → Tool 2 → Tool 3
   # Then test scaling with extracted recipe
   
   # Test Tool 1 → Tool 2 → Tool 3 → Tool 4
   # Then test validation with scaled recipe
   ```

5. **Integration Test**
   ```bash
   python3.11 tests/run_tests.py
   # Run all automated tests
   ```

### Phase 6: Documentation & Evaluation
- [ ] Create comprehensive README with installation and usage instructions
- [ ] Implement evaluation metrics and test cases for each tool
- [ ] Document tool specifications (inputs, outputs, error handling)
- [ ] Create example scripts demonstrating agent capabilities
- [ ] **FINAL VALIDATION**: Complete system test with all tools and help system

## Success Criteria
- **Tool 1**: ≥3 recipes found and extracted per search
- **Tool 2**: Accurate scaling + proper unit conversion
- **Tool 3**: Complete, well-formatted recipe with clear sections
- **Integration**: Robust error handling with graceful fallbacks

## Error Handling Strategy
- **Tool 1**: If no results → fail gracefully, suggest retry
- **Tool 2**: If scaling fails → try next recipe from Tool 1's list
- **Tool 3**: If validation fails → surface specific issues, try next recipe

## Development Approach
- Red-Green-Refactor methodology
- Test each tool thoroughly before moving to next
- Incremental validation at each step
- Focus on modularity and extensibility
