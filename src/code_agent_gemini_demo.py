#!/usr/bin/env python3

from smolagents import CodeAgent, Tool
from smolagents import OpenAIServerModel


# Define a simple calculator tool
class Calculator(Tool):
    name: str = "calculator"
    description: str = (
        "Computes the results of a mathematical expression."
        "The expression must be made in Python syntax."
    )
    inputs: dict = {
        "expression": {
            "type": "string",
            "description": "The Python expression to evaluate."
        }
    }
    output_type: dict = "string"

    def forward(self, expression: str) -> str:
        """
        Evaluates the mathematical python expression and returns the result.

        Args:
            expression: The python mathematical expression.

        Returns:
            The numerical result of evaluating the expression.
        """
        return str(eval(expression))


calculator_tool = Calculator()
tools = [ calculator_tool ]
additional_authorized_imports = []

import dotenv
import os
dotenv.load_dotenv()

model_id = os.getenv("MODEL_ID", "gemini-2.5-flash")
model = OpenAIServerModel(model_id=model_id,
                          api_base=os.getenv("GPT_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta/openai/"),
                          api_key=os.getenv("GEMINI_API_KEY"),
                          )
agent = CodeAgent(
    tools=tools,
    model=model,
    additional_authorized_imports=additional_authorized_imports,
    max_steps=3
)

answer = agent.run("What is 23 times 17 minus 42?")
print(f"Agent returned answer: {answer}")
