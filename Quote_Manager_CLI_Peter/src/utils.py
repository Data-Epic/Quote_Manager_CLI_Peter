import json
import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data")
data_path = os.path.join(data_dir, "quotes.json")


def lower_data(data_copy: dict) -> dict:

    """
    Function to convert all keys and values in the JSON data to lowercase

    Args:
    data_copy (dict): A dictionary containing the JSON data

    Returns:
    Dict: A dictionary containing the JSON data with all keys and values in lowercase

    """
    new_data = {}

    for category, records in data_copy.items():

        lower_category = category.lower()
        item_list = []
        for record in records:

            record_keys = record.keys()
            item = {}
            for key in record_keys:

                lower_key = key.lower()
                value = record[key]
                value = value.lower()
                item[lower_key] = value
            item_list.append(item)

            new_data[lower_category] = item_list

    return new_data


def load_data(file_path: str) -> dict:
    """
    Function to load data from the json file

    Args:
    file_path (str): Path to the json file containing quotes

    Returns:
    Dict: A dictionary containing the json data

    """

    if os.path.exists(file_path):

        if str(file_path).endswith(".json"):
            with open(file_path, "r", encoding="utf8") as f:
                data = json.load(f)

            # ensure all keys are in lowercase
            data_copy = data.copy()
            data = lower_data(data_copy)
            return data
        else:
            raise ValueError("Invalid file format. Only JSON files are allowed")

    else:
        raise ValueError("Invalid file path provided, File may not exist")


def query_existing_data(model: declarative_base, data: dict, db: Session) -> dict:
    """
    Function to query existing data in the database

    Args:
    model (declarative_base): The sqlalchemy model to query
    data (dict): The data to query
    db (Session): The sqlalchemy session object

    Returns:
    Dict: A dictionary containing the existing data, existing ids, record list and record ids
    """
    if isinstance(data, dict) is True:
        if isinstance(db, Session) is True:

            record_list = []
            for category, quotes in data.items():
                for quote in quotes:
                    quote["category"] = category
                    record_list.append(quote)

            for record in record_list:
                record["id"] = record_list.index(record) + 1
            record_ids = [record["id"] for record in record_list]

            existing_data = db.query(model).filter(model.id.in_(record_ids)).all()
            existing_ids = [record.id for record in existing_data]

            return {
                "existing_data": existing_data,
                "existing_ids": existing_ids,
                "record_list": record_list,
                "record_ids": record_ids,
            }
        else:
            raise ValueError(
                "Invalid database session. Database session must be a sqlalchemy session object"
            )
    else:
        raise ValueError("Invalid data format. Data argument must be a dictionary")
