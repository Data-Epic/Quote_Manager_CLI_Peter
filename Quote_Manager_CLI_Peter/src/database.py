from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base
from contextlib import contextmanager
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_path = "quotes.db"
sql_alchemy_database_url = f"sqlite:///{db_path}"
engine = create_engine(sql_alchemy_database_url)
Base.metadata.create_all(engine)

@contextmanager
def get_db():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=create_engine(sql_alchemy_database_url))
    db = SessionLocal()
    try:
        logger.info("Database session opened")
        yield db
    except Exception as e:
        logger.error(f"Error occurred during database operation: {str(e)}")
        raise
    finally:
        logger.info("Closing database session")
        db.close()

