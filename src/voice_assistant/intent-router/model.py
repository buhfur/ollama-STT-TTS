#!/usr/bin/env python3 
import asyncio
from ollama import AsyncClient
from typing import Dict,Any
import json

#OLLAMA_URL = "http://localhost:11434/api/generate"

async def ask_model(prompt: str,model_name: str = "BIR") -> Dict[str,Any]:
    """Makes asynchronous request to llm""" 
    print(f"Making request to model: {model_name}")
    try:
        response = await AsyncClient().generate(model=model_name,prompt=prompt, format='json')
        response = json.loads(response['response']) # Convert actual response into json 
        return response

    except Exception as e:
        print(f"Error making request to {model_name}: {e}")
        return {'intent': e}







if __name__ == '__main__':

    response = asyncio.run(
            ask_model("run a system update for me", model_name="BIR")
            )

    #print(response['intent'])
    #print(response['args'])
    print(response['args']['request'])
