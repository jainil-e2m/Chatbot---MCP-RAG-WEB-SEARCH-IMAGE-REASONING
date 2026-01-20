
print("Starting debug...")
try:
    print("Importing config...")
    from app.core import config
    print("Config OK")
except Exception as e:
    print(f"Config failed: {e}")

try:
    print("Importing model_router...")
    from app.core import model_router
    print("Model Router OK")
except Exception as e:
    print(f"Model Router failed: {e}")

try:
    print("Importing agent_factory...")
    from app.core import agent_factory
    print("Agent Factory OK")
except Exception as e:
    print(f"Agent Factory failed: {e}")

try:
    print("Importing rag...")
    from app.core import rag
    print("RAG OK")
except Exception as e:
    print(f"RAG failed: {e}")

try:
    print("Importing chat api...")
    from app.api import chat
    print("Chat API OK")
except Exception as e:
    print(f"Chat API failed: {e}")
