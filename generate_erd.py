from eralchemy import render_er
from app.models import Base

def main():
    print("Generating ERD from Python models...")
    try:
        # This looks at the code definitions, not the database!
        render_er(Base.metadata, 'entity_relation.png')
        print("Success! Created entity_relation.png")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
