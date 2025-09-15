# AI Chef Assistant - Development Checklist

## Project Overview
Building a multi-tooled AI chef assistant using smolagents framework with 3 specialized tools for recipe curation and modification.

## Tool Architecture
- **Tool 1**: Recipe Search & Extraction (with dietary filtering)
- **Tool 2**: Recipe Scaling & Unit Conversion (intelligent unit handling)
- **Tool 3**: Recipe Validation & Final Formatting (completeness & structure)

## Development Phases

### Phase 1: Foundation Setup
- [ ] Set up basic smolagents framework with 'Hello AI' validation
- [ ] Configure environment and dependencies
- [ ] Establish basic agent structure

### Phase 2: Tool 1 - Recipe Search & Extraction
- [ ] Build Tool 1: Recipe Search & Extraction with dietary filtering
- [ ] Implement search functionality with dietary restrictions
- [ ] Add recipe content extraction from search results
- [ ] Test Tool 1 with various dietary restrictions and validate ≥3 recipes returned
- [ ] Add error handling for no results scenarios

### Phase 3: Tool 2 - Recipe Scaling & Unit Conversion
- [ ] Build Tool 2: Recipe Scaling & Unit Conversion with intelligent unit handling
- [ ] Implement serving size scaling logic
- [ ] Add unit conversion capabilities (tbsp→cups, etc.)
- [ ] Test Tool 2 with different serving sizes and unit conversions
- [ ] Validate scaling accuracy and unit conversion logic

### Phase 4: Tool 3 - Recipe Validation & Final Formatting
- [ ] Build Tool 3: Recipe Validation & Final Formatting with completeness checks
- [ ] Implement recipe completeness validation (ingredients + steps)
- [ ] Add proper formatting and structure validation
- [ ] Test Tool 3 with incomplete recipes and validate proper formatting output
- [ ] Ensure clear section organization (ingredients, steps, etc.)

### Phase 5: Integration & Testing
- [ ] Full pipeline integration testing with error handling and fallback scenarios
- [ ] Test complete workflow: search → extract → scale → validate
- [ ] Implement fallback logic (try next recipe if current fails)
- [ ] Stress test with various edge cases

### Phase 6: Documentation & Evaluation
- [ ] Create comprehensive README with installation and usage instructions
- [ ] Implement evaluation metrics and test cases for each tool
- [ ] Document tool specifications (inputs, outputs, error handling)
- [ ] Create example scripts demonstrating agent capabilities

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
