from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# <user name>:<password>@url/<server name>
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.db_username}:{settings.db_password}@{settings.db_hostname}/{settings.db_name}'
# the engine is responsible for establishing the database connection
engine = create_engine(SQLALCHEMY_DATABASE_URL)
# creating the base classes for session and data model
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency function
# this function creates a new local session for each database connection request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
