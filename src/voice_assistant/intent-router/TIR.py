#!/usr/bin/env python3 
from typing import Dict,Any,Callable 
import asyncio 

# Tool intent router for automation tasks 
# Registry pattern for running specific tools related to terminal emulation  
 
# Decides what tool is going to be used for a specific command 
# Registry pattern 

# Dictionary that holds a str key and for the value , a function that takes a Dict[str, Any] as input
TOOL_REGISTRY: Dict[str, Callable[[str,str],None]] = {} 
# Registration decorator , receives res['intent'] from llm request 
def register_tool(tir_intent: str):
    def decorator(func: Callable[[str,str], None]):
        TOOL_REGISTRY[tir_intent] = func # Assign function as value to key "intent" 
        return func
    return decorator

# Accepts the output from the LIR llm , returns int with function status  
@register_tool("apt")
async def handle_apt_intent(command: str , args: str):
    """Run apt tool """
    # TODO: design some topology for running commands in a sandboxed environment 
    command = f"Command: {command}, args: {args}"
    return command # TODO: probably going to run some other or script idk atm 

# Core routing logic 
async def handle_tool(command: str, args: str) -> Callable[[str,str],None]:
    if command not in TOOL_REGISTRY:
        raise ValueError(f"Unsupported tool: {command}")
    # dynamic lookup and execution 
    handler = TOOL_REGISTRY[command]
    return await handler(command, args)


