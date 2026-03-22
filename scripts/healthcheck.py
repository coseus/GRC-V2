from app.db.session import engine
from sqlalchemy import text

def main():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("ok")

if __name__ == "__main__":
    main()
