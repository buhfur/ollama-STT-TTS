#!/usr/bin/env python3 
from typing import Dict,Any,Callable 

# Tool intent router for automation tasks 
# Registry pattern for running specific tools related to terminal emulation  
 
# Decides what tool is going to be used for a specific command 
# Regsitry pattern 
# Registry pattern 

# Dictionary that holds a str key and for the value , a function that takes a Dict[str, Any] as input
TOOL_REGISTRY: Dict[str, Callable[[str,str],int]] = {} 


# Registration decorator , receives res['intent'] from llm request 
def register_tool(tir_intent: str):
    def decorator(func: Callable[[str,str], int]):
        TOOL_REGISTRY[tir_intent] = func # Assign function as value to key "intent" 
        return func
    return decorator

# Accepts the output from the LIR llm , returns int with function status  
@register_tool("apt")
def handle_apt_intent(command: str , args: str):
    """Run apt tool """
    return args 




# Core routing logic 

def handle_tool(command: str, args: str):
    tool_name = bir_res['intent']
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"Unsupported tool: {tool_name}")



    # dynamic lookup and execution 
    handler = TOOL_REGISTRY[tool_name]
    handler()



