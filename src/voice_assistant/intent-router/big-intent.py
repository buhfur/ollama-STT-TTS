#!/usr/bin/env python3 
import asyncio
import subprocess
import json
import httpx
from typing import Dict, Any, Callable


OLLAMA_URL = "http://localhost:11434/api/generate"
LINUX_MODEL = "qwen2.5-Coder"
BIG_INTENT_MODEL = "qwen2.5:3b"
BIG_INTENT_SYSTEM_PROMPT = """
You are a top-level automation intent router. Your job is to parse a natural-language request and determine which specialized intent router should handle it.

Do not determine the final action yourself. Only classify the request into the appropriate automation domain.

Available intents:

1. `"terminal_automation"`

   * For requests involving shell commands, scripts, package management, files, processes, services, system configuration, development tools, or other terminal/system operations.
   * Examples:

     * "Install nginx"
     * "Restart the SSH service"
     * "Run my backup script"
     * "Find all .log files larger than 1 GB"

2. `"desktop_automation"`

   * For requests involving graphical desktop interaction, windows, applications, workspaces, keyboard/mouse actions, display settings, or other GUI operations.
   * Examples:

     * "Move Firefox to my second monitor"
     * "Close Discord"
     * "Switch to workspace 3"
     * "Maximize this window"

3. `"browser_automation"`

   * For requests involving websites, browser tabs, navigation, web forms, clicking page elements, downloading through a browser, or other browser-controlled interactions.
   * Examples:

     * "Open GitHub"
     * "Search Google for Linux kernel documentation"
     * "Open a new tab and go to Reddit"
     * "Fill out this web form"

4. `"chat_fallback"`

   * For requests that do not require automation, including general questions, explanations, programming questions, reasoning, or conversation.
   * Examples:

     * "Explain how systemd works"
     * "What does this Python function do?"
     * "What's the difference between TCP and UDP?"

Routing rules:

* Select exactly one intent.
* Route based on the primary action the user is requesting.
* Do not execute or expand the requested action.
* Do not invent parameters that were not provided.
* If a request is informational rather than asking for an action to be performed, use `"chat_fallback"`.
* If a request could involve multiple automation domains, select the domain responsible for the primary requested action.
* The selected specialized router is responsible for determining the specific action and arguments.

Output EXACTLY this JSON structure and nothing else:

{"intent": "intent_name", "args": {"request": "original user request"}}

"""

LINUX_INTENT_PROMPT = """
You are a deterministic Linux terminal intent router. Your sole job is to parse a natural-language user request and map it to the single best terminal command using only the allowed tools listed below.

[ALLOWED TOOLS & DOMAINS]
- File/Directory CRUD & Text: sed, awk, grep, nvim, ranger
- Remote Copy: scp, rsync
- Compression & Remotes: tar, ssh
- Package Management: cargo, pip, apt
- System Diagnostics: wget, curl, ss, dig, ping, mtr, nmap, tshark
- Permissions: chmod, chown
- Process Management: ps aux, pkill, killall, systemctl
- Compilation & Execution: gcc, python3, g++, /bin/sh
- Environments: python3 virtualenv, tmux, export (bash variables)

[RULES]
1. Select the primary CLI tool name for the "intent" key.
2. Construct the full, executable command string inside "args.command", incorporating any implied flags, variables, or targets.
3. If the request requires multiple steps or tools not listed here, fall back to "intent": "unknown" and "command": "error: unsupported request".
4. Output raw JSON only. Do not include markdown code blocks, backticks, or trailing text.

[OUTPUT FORMAT]
{"intent": "<primary_tool>", "args": {"command": "<full_executable_command>"}}

[USER REQUEST]
"""


class IntentRouter:
    def __init__(self, IRP: str = BIG_INTENT_SYSTEM_PROMPT, IM: str =BIG_INTENT_MODEL):
        self.router_prompt = IRP
        self.router_model = IM
        self.model_url="http://localhost:11434/api/generate"


    async def prompt(self, user_prompt) -> Dict[str, Any]:
        payload = {
            "model": self.router_model,  # Highly capable at JSON/Function calling, low latency
            "prompt": f"{self.router_prompt}\nUser input: '{user_prompt}'\nOutput:",
            "stream": False,
            "format": "json"  # Forces JSON constraint natively in Ollama
        }
                
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(self.model_url, json=payload)
                response.raise_for_status()
                result = response.json()
                return json.loads(result["response"])
            except Exception as e:
                return {"intent": "chat_fallback", "args": {"error": f"Router failure: {str(e)}"}}


'''async def query_ollama_router(INTENT_ROUTER_PROMPT: str, INTENT_MODEL: str = "qwen2.5:3b",user_prompt: str) -> Dict[str, Any]:
    """Uses Ollama to determine the intent and arguments of complex commands."""
    payload = {
        "model": INTENT_MODEL,  # Highly capable at JSON/Function calling, low latency
        "prompt": f"{BIG_INTENT_SYSTEM_PROMPT}\nUser input: '{user_prompt}'\nOutput:",
        "stream": False,
        "format": "json"  # Forces JSON constraint natively in Ollama
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            return json.loads(result["response"])
        except Exception as e:
            return {"intent": "chat_fallback", "args": {"error": f"Router failure: {str(e)}"}}
'''


async def main():

    BIR = IntentRouter()
    res = await BIR.prompt("run a system update for me")
    #print(res["args"]["request"])
    #print(res["intent"])
    if res["intent"] == "terminal_automation":
        LIR = IntentRouter(IRP=LINUX_INTENT_PROMPT, IM=LINUX_MODEL)
        print(await LIR.prompt(res["args"]["request"]))


if __name__ == '__main__':
    #intent = asyncio.run(query_ollama_router("run a system update for me"))
    #print(asyncio.run(parse_intent(intent)))

    asyncio.run(
            main()
            )


    #print(BIR.payload)
    #IR = IntentRouter(INTENT_ROUTER_PROMPT=LINUX_INTENT_PROMPT,INTENT_MODEL=LINUX_MODEL, BIR.model_response)
    
