import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("VITE_ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("Missing VITE_ANTHROPIC_API_KEY")

client = Anthropic(api_key=api_key)

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Say hello"}
    ],
)

print(message.content[0].text)