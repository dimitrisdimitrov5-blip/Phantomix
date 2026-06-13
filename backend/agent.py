import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are Phantomix, a powerful AI browser agent. 
You help users automate browser tasks like:
- Browsing and scraping websites
- Filling forms automatically
- Booking appointments
- Shopping online
- Any browser-based task

When given a task, break it down into clear browser actions and execute them step by step.
Always confirm what you did and report results clearly."""

async def run_agent(task: str, conversation_history: list = []):
    messages = conversation_history + [{"role": "user", "content": task}]
    
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    
    reply = response.content[0].text
    conversation_history.append({"role": "user", "content": task})
    conversation_history.append({"role": "assistant", "content": reply})
    
    return reply, conversation_history
