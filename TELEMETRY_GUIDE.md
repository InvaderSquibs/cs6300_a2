# 🔍 Phoenix Telemetry Developer Guide

## **Quick Start**

### **1. Start Phoenix Server**
```bash
python3.11 -m phoenix.server.main serve --port 6006
```

### **2. Enable Telemetry**
```bash
export ENABLE_TELEMETRY=true
python3.11 src/chef_agent.py "I'd like some pancakes for 8 people" --restrictions "vegan"
```

### **3. View Dashboard**
Open http://localhost:6006 in your browser

---

## **📊 Understanding the Dashboard**

### **Main Views**

**1. Traces Tab**
- Shows individual request flows
- Each trace represents one complete recipe request
- Click on traces to see detailed spans

**2. Spans Tab**
- Shows individual tool executions
- Each span represents one tool call
- Filter by tool name, duration, status

**3. Evaluations Tab**
- Shows performance metrics and evaluations
- Success rates, error analysis

---

## **🔍 Reading Tool Execution Traces**

### **Trace Structure**
```
📋 Recipe Request (Root Span)
├── 🔍 recipe_search (Search Tool)
├── 📄 recipe_extraction_llm (Extraction Tool)
├── ⚖️ recipe_scaling_llm (Scaling Tool)
└── 📝 recipe_formatter_llm (Formatter Tool)
```

### **Key Metrics to Look For**

#### **🔍 Search Tool Metrics**
- **`search.query`**: What was searched for
- **`search.results_count`**: How many recipes found
- **`search.dietary_restrictions`**: Applied filters
- **`search.filtered_count`**: Recipes after filtering
- **Duration**: How long search took

#### **📄 Extraction Tool Metrics**
- **`extraction.url`**: Which recipe was extracted
- **`extraction.ingredients_count`**: Number of ingredients found
- **`extraction.instructions_count`**: Number of steps found
- **`extraction.servings`**: Original serving size
- **`extraction.prep_time`**: Preparation time
- **`extraction.cook_time`**: Cooking time
- **`extraction.dietary_tags`**: Detected dietary tags

#### **⚖️ Scaling Tool Metrics**
- **`scaling.original_servings`**: Original recipe servings
- **`scaling.target_servings`**: Target servings requested
- **`scaling.scaling_factor`**: Mathematical scaling factor
- **`scaling.scaling_method`**: Method used (proportional, time_adjusted)
- **`scaling.unit_conversions_count`**: Number of unit conversions

#### **📝 Formatter Tool Metrics**
- **`formatter.recipe_title`**: Recipe title being formatted
- **`formatter.filename`**: Generated markdown filename
- **`formatter.file_size`**: Size of generated file
- **`formatter.format_style`**: Formatting style used

---

## **🐛 Debugging Common Issues**

### **1. Search Tool Issues**
**Problem**: No recipes found
- Check `search.results_count` = 0
- Look at `search.query` - is it too specific?
- Check `search.dietary_restrictions` - too restrictive?

**Problem**: Too many irrelevant results
- Check `search.filtered_count` vs `search.results_count`
- Look at filtering effectiveness

### **2. Extraction Tool Issues**
**Problem**: Extraction fails
- Check `extraction.url` - is it accessible?
- Look for HTTP errors in span attributes
- Check if site blocks our requests

**Problem**: Missing ingredients/instructions
- Check `extraction.ingredients_count` and `extraction.instructions_count`
- Low counts might indicate parsing issues

### **3. Scaling Tool Issues**
**Problem**: Scaling not working
- Check `scaling.scaling_factor` - should be > 1.0 for upscaling
- Verify `scaling.original_servings` vs `scaling.target_servings`
- Look for scaling method used

**Problem**: Unit conversion issues
- Check `scaling.unit_conversions_count`
- Look for conversion errors in span attributes

### **4. Formatter Tool Issues**
**Problem**: File not generated
- Check `formatter.filename` and `formatter.file_size`
- Look for file system errors
- Verify output directory permissions

---

## **📈 Performance Analysis**

### **Timing Analysis**
1. **Total Pipeline Duration**: From root span
2. **Tool Execution Times**: Individual span durations
3. **Bottlenecks**: Which tool takes longest?

### **Success Rate Analysis**
1. **Overall Success Rate**: Percentage of successful traces
2. **Tool Success Rates**: Individual tool success percentages
3. **Error Patterns**: Common failure points

### **Resource Usage**
1. **Token Usage**: Input/output tokens per tool
2. **Memory Usage**: File sizes, data volumes
3. **Network Calls**: HTTP requests, API calls

---

## **🔧 Advanced Filtering**

### **Filter by Tool**
```
tool.name = "recipe_scaling_llm"
```

### **Filter by Duration**
```
duration > 10s
```

### **Filter by Status**
```
status = "ERROR"
```

### **Filter by Attributes**
```
scaling.scaling_factor > 2.0
extraction.ingredients_count > 10
```

---

## **📊 Custom Queries**

### **Find High-Scaling Recipes**
```
scaling.scaling_factor > 3.0
```

### **Find Extraction Failures**
```
tool.name = "recipe_extraction_llm" AND status = "ERROR"
```

### **Find Large Recipe Files**
```
formatter.file_size > 5000
```

### **Find Long-Running Requests**
```
duration > 30s
```

---

## **🚨 Alerting & Monitoring**

### **Key Metrics to Monitor**
1. **Error Rate**: Should be < 5%
2. **Average Duration**: Should be < 30s
3. **Success Rate**: Should be > 95%
4. **Scaling Accuracy**: Factor should match expected ratio

### **Common Alerts**
- High error rate on extraction tool
- Scaling factor significantly off from expected
- Very long execution times
- Low success rates

---

## **💡 Best Practices**

### **1. Regular Monitoring**
- Check dashboard daily for error patterns
- Monitor performance trends over time
- Set up alerts for critical metrics

### **2. Debugging Workflow**
1. Start with trace view to see overall flow
2. Drill down to problematic spans
3. Check span attributes for specific errors
4. Use filtering to find similar issues

### **3. Performance Optimization**
1. Identify slowest tools in pipeline
2. Look for patterns in long-running requests
3. Optimize based on telemetry insights
4. A/B test improvements

---

## **🔗 Useful Links**

- **Phoenix Documentation**: https://docs.phoenix.arize.com/
- **OpenTelemetry Guide**: https://opentelemetry.io/docs/
- **SmolAgents Telemetry**: https://github.com/huggingface/smolagents

---

## **📞 Support**

If you encounter issues with telemetry:
1. Check Phoenix server is running on port 6006
2. Verify `ENABLE_TELEMETRY=true` is set
3. Check browser console for JavaScript errors
4. Review telemetry configuration in `src/telemetry_config.py`
