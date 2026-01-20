
print("Testing ChatOpenAI import...")
try:
    from langchain_openai import ChatOpenAI
    print("ChatOpenAI imported successfully!")
except Exception as e:
    print(f"ChatOpenAI import failed: {e}")
