import asyncio
from model import ask_model

# Ties all the functionality from all prior scripts 




# Function that acts as facade to the logic behind the intent router , receives transcription as input 
async def perform_task(prompt: str): 

    get_intent = await ask_model(prompt)

    get_task = process_intent(get_intent)

    run_task = run_task(get_task)
    


if __name__ == '__main__':

    prompt = "Containerize this python3 project for me."
    # Get response from BIR 
    # Get model name 
    #get_tool = await process_intent(intent)
