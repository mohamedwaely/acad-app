import logging
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
import urllib.parse

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# URL-encode database credentials
db_password = urllib.parse.quote_plus(os.getenv('DB_PASSWORD'))
host = urllib.parse.quote_plus(os.getenv('DB_HOST'))
port = urllib.parse.quote_plus(os.getenv('DB_PORT'))
db_name = urllib.parse.quote_plus(os.getenv('DB_NAME'))
db_user = urllib.parse.quote_plus(os.getenv('DB_USER'))

DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{db_user}:{db_password}@"
    f"{host}:{port}/"
    f"{db_name}?sslmode=require"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Provide a database session for dependency injection."""
    db = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")
    finally:
        if db:
            db.close()