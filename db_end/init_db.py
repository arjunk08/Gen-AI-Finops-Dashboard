from db_end.db1 import engine, Base
import db_end.models

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    create_tables()