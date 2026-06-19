import os
import anthropic
import traceback

try:
    key = os.getenv("VITE_ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("VITE_ANTHROPIC_API_KEY is not set")

    print("Loaded prefix:", repr(key[:12]))
    print("Full repr starts correctly:", key.startswith("sk-ant-"))

    client = anthropic.Anthropic(api_key=key)

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=20,
        messages=[{"role": "user", "content": "Reply only with OK"}],
    )

    print("SUCCESS:", msg.content[0].text)

except Exception as e:
    print("ERROR:", e)
    traceback.print_exc()