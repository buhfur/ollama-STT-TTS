#!/usr/bin/env python3 
import asyncio
from model import ask_model
from typing import Dict,Any,Tuple
#from BIR import process_intent
from TIR import handle_tool


# Takes prompt as input , returns full response from BIR in Dict[str, Any] 
async def get_BIR_response(prompt: str) -> Dict[str, Any]:
    return await ask_model(prompt)


# Extracts prompt and intent from the BIR llm response , returns the response  
async def get_TIR_response(BIR_output: Dict[str, Any]) -> Dict[str, Any]:
    model = BIR_output['intent']
    prompt = BIR_output['args']['request']
    return await ask_model(prompt, model_name=model)


# Ties all the functionality from all prior scripts 
# Function that acts as facade to the logic behind the intent router , receives transcription as input 
async def parse_intent(prompt: str) -> Tuple[str,str]:
    # Gets response from BIR 
    bir = await get_BIR_response(prompt)
    tir = await get_TIR_response(bir)


# test function  
async def main(): 
    prompt = "Run a system update for me"
    response = await parse_intent(prompt)
    print(response)


if __name__ == '__main__':

    asyncio.run(main())


    # Get response from BIR 
    # Get model name 
    #get_tool = await process_intent(intent)
