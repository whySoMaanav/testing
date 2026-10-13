import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'risk_directory.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Using SQLAlchemy. Check_same_thread=False is needed for SQLite in multithreaded environments like Streamlit.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
