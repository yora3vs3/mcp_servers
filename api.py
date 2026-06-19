import os

key = os.getenv("ANTHROPIC_API_KEY")
print("Loaded key prefix:", repr(key[:12]) if key else "None")