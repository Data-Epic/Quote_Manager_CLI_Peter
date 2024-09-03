import json 
from src.models import Quote
from src.database import get_db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data")
data_path = os.path.join(data_dir, "quotes.json")

def load_data(file_path:str) -> dict:
    """
    Function to load data from the json file
    """

    if os.path.exists(file_path):

        if str(file_path).endswith(".json"):
            with open(file_path, "r", encoding="utf8") as f:
                data = json.load(f)

            return data
        else:
            raise ValueError("Invalid file format. Only JSON files are allowed")
    
    else:
        raise ValueError("Invalid file path provided, File may not exist")

def query_existing_data(model:declarative_base,
                        data:dict,
                        db: Session) -> dict:
    """
    Function to query existing data in the database
    """
    if isinstance(data, dict) == True:
        if isinstance(db, Session) == True:
        
            record_list = []
            for category, quotes in data.items():
                for quote in quotes:
                    quote['category'] = category
                    record_list.append(quote)
            
            for record in record_list:
                record["id"] = record_list.index(record) + 1
            record_ids = [record["id"] for record in record_list]

            existing_data = db.query(model).filter(model.id.in_(record_ids)).all()
            existing_ids = [record.id for record in existing_data]
            
            return {
                "existing_data": existing_data, 
                    "existing_ids":existing_ids,
                    "record_list": record_list,
                    "record_ids": record_ids
                    }
        else:
            raise ValueError("Invalid database session. Database session must be a sqlalchemy session object")
    else:
        raise ValueError("Invalid data format. Data argument must be a dictionary")

