#!/usr/bin/env python3.11
"""
LLM-First Recipe Formatter Tool

This tool uses the LLM's natural language understanding to format recipes
into beautiful markdown files that read like cookbook recipes, with intelligent
content filtering to remove irrelevant information.
"""

from smolagents import Tool
import json
import time
import os
from openai import OpenAI

# Telemetry imports (optional)
try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False


class RecipeFormatterLLMTool(Tool):
    """
    LLM-powered recipe formatter that creates beautiful markdown recipe files
    with intelligent content filtering and cookbook-style formatting.
    
    Telemetry Tracking:
    - formatter.recipe_title: Recipe title being formatted
    - formatter.filename: Generated markdown filename
    - formatter.file_size: Size of generated markdown file
    - formatter.format_style: Formatting style used
    - formatter.content_filtering: Content filtering applied
    - formatter.success_rate: Formatting success percentage
    """
    
    name: str = "recipe_formatter_llm"
    description: str = (
        "Formats recipes into beautiful markdown files using LLM natural language understanding. "
        "Creates cookbook-style recipes with proper structure, headers, and formatting. "
        "Intelligently filters out irrelevant content and focuses on essential recipe information. "
        "Outputs are saved as .md files in the 'results/recipes/' directory with clean, professional formatting."
    )
    output_type: str = "string"
    
    def __init__(self):
        super().__init__()
        # Initialize OpenAI client for LLM calls
        self.client = OpenAI(
            base_url="http://192.168.1.27:1234/v1",
            api_key="dummy"  # Not needed for local server
        )
    
    inputs: dict = {
        "recipe_data": {
            "type": "string", 
            "description": "JSON string containing the recipe data to format"
        },
        "output_filename": {
            "type": "string", 
            "description": "Filename for the markdown file (e.g., 'vegan_pancakes.md')",
            "nullable": True
        },
        "format_style": {
            "type": "string", 
            "description": "Formatting style: 'cookbook' (default), 'simple', or 'detailed'",
            "nullable": True
        }
    }
    
    def forward(self, recipe_data: str, output_filename: str = None, format_style: str = "cookbook") -> str:
        """
        Format recipe into beautiful markdown file using LLM.
        
        Args:
            recipe_data (str): JSON string containing recipe data
            output_filename (str): Filename for the markdown file (optional, auto-generated if None)
            format_style (str): Formatting style ('cookbook', 'simple', 'detailed')
            
        Returns:
            str: JSON string with formatting result and file path
            
        Raises:
            ValueError: If recipe data is invalid
            IOError: If file writing fails
            
        Example:
            >>> tool = RecipeFormatterLLMTool()
            >>> result = tool.forward(recipe_json, "vegan_pancakes.md")
            >>> data = json.loads(result)
            >>> print(data["formatted_recipe"]["file_path"])
            results/recipes/vegan_pancakes.md
            
        Note:
            The formatted markdown file is automatically saved to the 'results/recipes/' directory.
            If output_filename is None, a clean filename is generated from the recipe title.
        """
        try:
            # Parse recipe data
            recipe = json.loads(recipe_data)
            
            if not recipe.get('success') or not recipe.get('recipe'):
                return json.dumps({
                    "success": False,
                    "error": "Invalid recipe data provided",
                    "original_recipe": recipe
                })
            
            recipe_info = recipe['recipe']
            
            # Generate filename if not provided
            if not output_filename:
                output_filename = self._generate_filename(recipe_info)
            
            # Use LLM to format the recipe
            markdown_content = self._format_with_llm(recipe_info, format_style)
            
            # Write to file
            file_path = self._write_markdown_file(markdown_content, output_filename)
            
            return json.dumps({
                "success": True,
                "formatted_recipe": {
                    "title": recipe_info.get('title', 'Unknown Recipe'),
                    "filename": output_filename,
                    "file_path": file_path,
                    "format_style": format_style,
                    "markdown_content": markdown_content
                },
                "formatting_info": {
                    "timestamp": int(time.time()),
                    "formatting_method": "llm_natural_language",
                    "content_filtering": "intelligent_llm_filtering",
                    "file_size": len(markdown_content)
                }
            })
            
        except json.JSONDecodeError as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to parse recipe data: {str(e)}",
                "original_recipe": recipe_data
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Formatting failed: {str(e)}",
                "original_recipe": recipe_data
            })
    
    def _format_with_llm(self, recipe: dict, format_style: str) -> str:
        """
        Use LLM to format recipe into beautiful markdown.
        
        Args:
            recipe (dict): Recipe data
            format_style (str): Formatting style
            
        Returns:
            str: Formatted markdown content
        """
        # Prepare the recipe data for the LLM
        recipe_text = self._format_recipe_for_llm(recipe)
        
        style_instructions = {
            "cookbook": "Format like a professional cookbook with elegant headers, clear sections, and beautiful typography",
            "simple": "Format in a clean, simple style with minimal decoration but clear structure",
            "detailed": "Format with comprehensive details, tips, and extensive formatting",
            "blogger": "Format like a heartfelt personal blog post with a long, emotional story about life, family, memories, and why this recipe means so much. The story should be drawn out, over-the-top, barely relate to the recipe, and end with 'anyways here's that recipe'. Make it very bloggy and personal."
        }
        
        prompt = f"""You are a professional recipe formatter. Create a beautiful markdown recipe file.

RECIPE DATA:
{recipe_text}

FORMATTING STYLE: {format_style}
STYLE INSTRUCTIONS: {style_instructions.get(format_style, style_instructions['cookbook'])}

INSTRUCTIONS:
1. Create a beautiful, well-structured markdown recipe
2. Use proper markdown headers, lists, and formatting
3. Include all essential recipe information
4. Filter out any irrelevant or redundant information
5. Make it read like a professional cookbook recipe
6. Use emojis sparingly and appropriately
7. Ensure proper markdown syntax
8. Include a clear title, description, ingredients list, and step-by-step instructions
9. Add timing information in a clear, readable format
10. Include serving information and dietary tags if available
11. Add a source link at the bottom of the recipe if URL is available

FORMATTING REQUIREMENTS:
- Use # for main title
- Use ## for major sections (Ingredients, Instructions, etc.)
- Use ### for subsections if needed
- Use - for ingredient lists
- Use numbered lists for instructions
- Use **bold** for important information
- Use *italics* for emphasis
- Include proper spacing and line breaks
- Make it visually appealing and easy to read
- If a URL is provided in the recipe data, add a "Source" section at the bottom with the link

SOURCE LINK FORMATTING:
- Add a "## Source" section at the very end of the recipe
- Format the link as: [Original Recipe URL](URL)
- Only include this section if a valid URL is available

Return ONLY the markdown content, no other text or explanation."""

        try:
            response = self.client.chat.completions.create(
                model="qwen/qwen3-4b-2507",
                messages=[
                    {"role": "system", "content": "You are a professional recipe formatter. Create beautiful, well-structured markdown recipes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.3
            )
            
            # Get the formatted content
            markdown_content = response.choices[0].message.content.strip()
            
            # Clean up any extra text that might have been included
            if markdown_content.startswith('```markdown'):
                markdown_content = markdown_content[11:]
            if markdown_content.endswith('```'):
                markdown_content = markdown_content[:-3]
            
            return markdown_content.strip()
                
        except Exception as e:
            # Fallback to basic formatting if LLM fails
            return self._fallback_formatting(recipe)
    
    def _format_recipe_for_llm(self, recipe: dict) -> str:
        """
        Format recipe data for LLM processing.
        
        Args:
            recipe (dict): Recipe data
            
        Returns:
            str: Formatted recipe text
        """
        lines = []
        
        # Title and basic info
        lines.append(f"Title: {recipe.get('title', 'Unknown Recipe')}")
        lines.append(f"Description: {recipe.get('description', 'No description available')}")
        lines.append(f"Servings: {recipe.get('servings', 'Unknown')}")
        lines.append(f"Prep Time: {recipe.get('prep_time', 'Unknown')}")
        lines.append(f"Cook Time: {recipe.get('cook_time', 'Unknown')}")
        lines.append(f"Total Time: {recipe.get('total_time', 'Unknown')}")
        lines.append(f"Difficulty: {recipe.get('difficulty', 'Unknown')}")
        lines.append(f"Dietary Tags: {', '.join(recipe.get('dietary_tags', []))}")
        lines.append(f"Source: {recipe.get('source', 'Unknown')}")
        lines.append(f"URL: {recipe.get('url', 'No URL available')}")
        lines.append("")
        
        # Ingredients
        lines.append("INGREDIENTS:")
        if 'ingredients' in recipe:
            for ingredient in recipe['ingredients']:
                if isinstance(ingredient, dict):
                    lines.append(f"- {ingredient.get('ingredient', 'Unknown ingredient')}")
                else:
                    lines.append(f"- {ingredient}")
        lines.append("")
        
        # Instructions
        lines.append("INSTRUCTIONS:")
        if 'instructions' in recipe:
            for instruction in recipe['instructions']:
                if isinstance(instruction, dict):
                    step_num = instruction.get('step', '?')
                    instruction_text = instruction.get('instruction', 'Unknown instruction')
                    lines.append(f"{step_num}. {instruction_text}")
                else:
                    lines.append(f"- {instruction}")
        
        return "\n".join(lines)
    
    def _generate_filename(self, recipe: dict) -> str:
        """
        Generate a filename for the recipe markdown file.
        
        Args:
            recipe (dict): Recipe data
            
        Returns:
            str: Generated filename
        """
        title = recipe.get('title', 'unknown_recipe')
        
        # Clean the title for filename
        import re
        clean_title = re.sub(r'[^\w\s-]', '', title.lower())
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        clean_title = clean_title.strip('_')
        
        # Limit length
        if len(clean_title) > 50:
            clean_title = clean_title[:50]
        
        return f"{clean_title}.md"
    
    def _write_markdown_file(self, content: str, filename: str) -> str:
        """
        Write markdown content to file.
        
        Args:
            content (str): Markdown content
            filename (str): Filename
            
        Returns:
            str: Full file path
        """
        # Create results/recipes directory if it doesn't exist
        results_dir = "results/recipes"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        
        # Ensure filename has .md extension
        if not filename.endswith('.md'):
            filename += '.md'
        
        # Write file
        file_path = os.path.join(results_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def _fallback_formatting(self, recipe: dict) -> str:
        """
        Fallback formatting if LLM fails.
        
        Args:
            recipe (dict): Recipe data
            
        Returns:
            str: Basic markdown content
        """
        lines = []
        
        # Title
        lines.append(f"# {recipe.get('title', 'Unknown Recipe')}")
        lines.append("")
        
        # Description
        if recipe.get('description'):
            lines.append(f"*{recipe['description']}*")
            lines.append("")
        
        # Basic info
        lines.append("## Recipe Information")
        lines.append(f"- **Servings:** {recipe.get('servings', 'Unknown')}")
        lines.append(f"- **Prep Time:** {recipe.get('prep_time', 'Unknown')}")
        lines.append(f"- **Cook Time:** {recipe.get('cook_time', 'Unknown')}")
        lines.append(f"- **Total Time:** {recipe.get('total_time', 'Unknown')}")
        lines.append(f"- **Difficulty:** {recipe.get('difficulty', 'Unknown')}")
        
        if recipe.get('dietary_tags'):
            lines.append(f"- **Dietary Tags:** {', '.join(recipe['dietary_tags'])}")
        
        lines.append("")
        
        # Ingredients
        lines.append("## Ingredients")
        if 'ingredients' in recipe:
            for ingredient in recipe['ingredients']:
                if isinstance(ingredient, dict):
                    lines.append(f"- {ingredient.get('ingredient', 'Unknown ingredient')}")
                else:
                    lines.append(f"- {ingredient}")
        lines.append("")
        
        # Instructions
        lines.append("## Instructions")
        if 'instructions' in recipe:
            for instruction in recipe['instructions']:
                if isinstance(instruction, dict):
                    step_num = instruction.get('step', '?')
                    instruction_text = instruction.get('instruction', 'Unknown instruction')
                    lines.append(f"{step_num}. {instruction_text}")
                else:
                    lines.append(f"- {instruction}")
        
        return "\n".join(lines)
