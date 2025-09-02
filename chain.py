# chain.py - Converted from chain.ipynb notebook
# This script demonstrates building a simple chain in LangGraph with messages, chat models, tools, and reducers.

# Install required packages (run this manually if needed):
# pip install langchain_openai langchain_core langgraph

import os
import getpass
from pprint import pprint
from typing_extensions import TypedDict
from typing import Annotated
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState, StateGraph, START, END

# Set up OpenAI API key
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

# Load chat model
llm = ChatOpenAI(model="gpt-4o")

# Define tool function
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

# Bind tools to LLM
llm_with_tools = llm.bind_tools([multiply])

# Define MessagesState with reducer
class MessagesState(MessagesState):
    # Add any keys needed beyond messages, which is pre-built
    pass

# Node function
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_edge(START, "tool_calling_llm")
builder.add_edge("tool_calling_llm", END)
graph = builder.compile()

# Main execution
if __name__ == "__main__":
    # Example 1: Hello (no tool call)
    print("Example 1: Hello!")
    messages = graph.invoke({"messages": HumanMessage(content="Hello!")})
    for m in messages['messages']:
        m.pretty_print()

    print("\n" + "="*50 + "\n")

    # Example 2: Multiply (with tool call)
    print("Example 2: Berapa 2 dikali 3?")
    messages = graph.invoke({"messages": HumanMessage(content="Berapa 2 dikali 3")})
    for m in messages['messages']:
        m.pretty_print()

    # Optional: Test tool call directly
    print("\n" + "="*50 + "\n")
    print("Direct tool call test:")
    tool_call = llm_with_tools.invoke([HumanMessage(content="Berapa 2 dikali 3", name="Lance")])
    print("Tool calls:", tool_call.tool_calls)
