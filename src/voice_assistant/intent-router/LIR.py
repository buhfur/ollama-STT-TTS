from typing import Dict,Any,Callable 
# Decides what tool is going to be used for a specific command 
# Regsitry pattern 
# Registry pattern 

# Dictionary that holds a str key and for the value , a function that takes a Dict[str, Any] as input
AUTOMATION_REGISTRY: Dict[str, Callable[[Dict[str, Any], None]]] = {} 


# Registration decorator , receives res['intent'] from llm request 
def register_intent(intent: str) 
    def decorator(func: Callable[[Dict[str, Any],None]]):
        AUTOMATION_REGISTRY[intent] = func # Assign function as value to key "intent" 
        return func
    return decorator

# Accepts the output from the BIR llm prompt as input , outputs the model_name & prompt to get the tool 
@register_intent("terminal_automation")
def handle_apt_intent(bir_intent: Dict[str, Any]) -> str:
    """Make async request to llm model that would translate the intent into a command to run"""
    return "LIR"




# Core routing logic 

def process_intent(method: str, prompt: str):
    if method not in AUTOMATION_REGISTRY:
        raise ValueError(f"Unsupported payment method: {method}")



    # dynamic lookup and execution 
    handler = AUTOMATION_REGISTRY[method]
    handler(prompt)



