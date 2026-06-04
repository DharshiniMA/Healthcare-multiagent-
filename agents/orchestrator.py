from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
import os

from agents.tools import book_appointment, set_reminder, get_patient_records
from agents.doctor_agent import search_doctors

# Ensure the model uses tools
tools = [search_doctors, book_appointment, set_reminder, get_patient_records]
tool_node = ToolNode(tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def create_agent():
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
    llm_with_tools = llm.bind_tools(tools)
    
    def chatbot(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)
    
    # Define routing logic
    def route_tools(state: State):
        if isinstance(state, list):
            ai_message = state[-1]
        elif isinstance(state, dict) and "messages" in state:
            ai_message = state["messages"][-1]
        else:
            return END
            
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return END
        
    graph_builder.add_conditional_edges("chatbot", route_tools, {"tools": "tools", END: END})
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    
    return graph_builder.compile()

graph = create_agent()

def process_query(user_query: str) -> str:
    state = {"messages": [HumanMessage(content=user_query)]}
    for event in graph.stream(state):
        for value in event.values():
            if "messages" in value:
                last_message = value["messages"][-1]
                # If it's a tool response, we wait for the AI to interpret it
                # We return the AI's final text response.
    
    # Retrieve the final state to get the AI's final message
    final_state = graph.invoke(state)
    return final_state["messages"][-1].content
