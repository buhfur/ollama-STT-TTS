#!/usr/bin/env python3 
#import subprocess
#import json
#import httpx
import asyncio
from ollama import AsyncClient
from typing import Dict,Any
import json
OLLAMA_URL = "http://localhost:11434/api/generate"


async def ask_model(prompt: str,model_name: str = "BIR") -> Dict[str,Any]:
    """Makes asynchronous request to llm""" 
    print(f"Making request to model: {model_name}")
    try:
        response = await AsyncClient().generate(model=model_name,prompt=prompt)

        # Convert actual response into json 
        response = json.loads(response['response'])
        #print(f"\n\nModel {model_name}\nresponse: {response}\ntype: {type(response)}\n\n")
        return response
        #return response

    except Exception as e:
        print(f"Error making request to {model_name}: {e}")
        return {'intent': e}







if __name__ == '__main__':

    asyncio.run(
            main()
            )


    
