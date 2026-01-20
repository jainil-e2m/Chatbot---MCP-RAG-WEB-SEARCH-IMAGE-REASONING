
from app.core.database import supabase
import sys

def test_db():
    print("Testing Supabase Connection...")
    try:
        # Try to selecting from a known table or users
        print("Selecting from conversations table...")
        res = supabase.table("conversations").select("count").execute()
        print(f"Result: {res.data}")
        return True
    except Exception as e:
        print(f"Database Error: {e}")
        return False

if __name__ == "__main__":
    success = test_db()
    if not success:
        sys.exit(1)
