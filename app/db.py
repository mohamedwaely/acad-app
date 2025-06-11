from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import urllib.parse

import os

load_dotenv()

db_password = urllib.parse.quote_plus(os.getenv('db_password'))
dbURL = (
    f"postgresql+psycopg://"
    f"{os.getenv('db_user')}:{db_password}@"
    f"{os.getenv('db_host')}:{os.getenv('db_port')}/"
    f"{os.getenv('db_name')}?sslmode=require"
)

engine = create_engine(dbURL)

try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()