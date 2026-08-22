
import asyncio
import sys 
from typing import Dict,Any,Callable 
from model import ask_model
from TIR import handle_tool

# Big intent router: Classifies which model needs to be used for a specific prompt  
# Registry pattern 

# Dictionary that holds a str key and for the value , a function that takes a Dict[str, Any] as input
AUTOMATION_REGISTRY: Dict[str, Callable[str, None]] = {} 


# Registration decorator , receives res['intent'] from llm request 
def register_intent(intent: str): 
    def decorator(func: Callable[str,None]):
        AUTOMATION_REGISTRY[intent] = func # Assign function as value to key "intent" 
        return func
    return decorator

# Accepts the output from the BIR llm prompt as input , returns the response from LIR
@register_intent("terminal_automation")
async def handle_terminal_intent(prompt: str) -> Dict[str, Any]:
    """Make async request to llm model that would translate the intent into a command to run"""
    # extract prompt from BIR resp
    TIR_get_intent = await ask_model(prompt[''], model_name="LIR")
    print(f"Response from LIR: {TIR_get_intent}")
    return TIR_get_intent


    
    

    




# Core routing logic 

# Takes prompt as input from transcription , runs command through whichever IR , then returns whether the tool executed without issue 
async def process_intent(prompt):
    BIR_get_intent = await ask_model(prompt)

    method = BIR_get_intent['intent']

    print(method)
    if method not in AUTOMATION_REGISTRY:
        raise ValueError(f"Unsupported intent: {method}")



    # dynamic lookup and execution 
    handler = AUTOMATION_REGISTRY[method]
    return await handler(prompt) # stores response from LIR 
    #tool_response = handle_tool(tool['intent'],tool['args'])


async def main():
    prompt = "run a system update for me."

    await process_intent(prompt)



if __name__ == '__main__': 

    asyncio.run(main())





