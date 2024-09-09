import json
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from quote_manager_cli_peter.models import Quote
from quote_manager_cli_peter.utils import load_data, query_existing_data


@pytest.fixture
def create_valid_json(tmp_path: str) -> str:

    """
    Test to create a valid json file

    Args:
    tmp_path: A temporary path to create the file

    Returns:
    str: The path to the created file

    """

    data = {"category1": [{"quote": "This is a test quote", "author": "Test Author"}]}

    file_path = tmp_path / "valid.json"
    with open(file_path, "w", encoding="utf8") as f:
        json.dump(data, f)

    print("file_path", file_path)
    return file_path


@pytest.fixture
def create_invalid_json(tmp_path: str) -> str:
    """
    Test to create an invalid json file

    Args:
    tmp_path: A temporary path to create the file

    Returns:
    str: The path to the created file

    """
    data = {"category1": [{"quote": "This is a test quote", "author": "Test Author"}]}
    file_path = tmp_path / "invalid.txt"
    with open(file_path, "w", encoding="utf8") as f:
        json.dump(data, f)
    return file_path


def test_load_data_valid_file(create_valid_json: str) -> None:
    """
    Test to load data from a valid json file

    Args:
    create_valid_json: A valid json file

    Returns: None

    """
    data = load_data(create_valid_json)
    print("data", data)
    assert data is not None
    assert isinstance(data, dict)
    assert len(data) == 1
    assert "category1" in data
    assert len(data["category1"]) == 1
    assert data["category1"][0]["quote"] == "this is a test quote"
    assert data["category1"][0]["author"] == "test author"


def test_load_data_invalid_file(create_invalid_json: str) -> None:
    """
    Test to load data from an invalid file format

    Args:
    create_invalid_json: An invalid file format

    Returns: None

    """
    with pytest.raises(ValueError) as e:
        load_data(create_invalid_json)
    assert str(e.value) == "Invalid file format. Only JSON files are allowed"


def test_load_data_invalid_path() -> None:
    """
    Test to load data from an invalid file path

    Returns: None

    """
    with pytest.raises(ValueError) as e:
        load_data("invalid_path.json")
    assert str(e.value) == "Invalid file path provided, File may not exist"


@patch("sqlalchemy.orm.Session", autospec=True)
def test_query_existing_data(mock_session) -> None:

    """ "
    Test to query existing data in the database

    Args:
    mock_session: A mock session object

    Returns: None

    """

    # setup a mock data and database session
    mock_data = {
        "inspirational": [
            {
                "quote": "This is an inspirational quote",
                "author": "Inspirational Author",
            }
        ]
    }

    mock_db_session = MagicMock(spec=Session)
    mock_session.return_value.__enter__.return_value = mock_db_session
    mock_db_session.query.return_value.filter.return_value.all.return_value = []
    result = query_existing_data(Quote, mock_data, mock_session)
    print("result", result)

    assert result is not None
    assert isinstance(result, dict)
    assert "existing_ids" in result
    assert result["existing_ids"] == []
    assert "record_list" in result
    assert len(result["record_list"]) == 1
    assert "record_ids" in result
    assert result["record_ids"] == [1]
