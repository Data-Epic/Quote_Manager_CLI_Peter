import ast
import json
from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from src.cli import add, generate, import_quotes, list_quotes
from src.models import Quote


@pytest.fixture
def sample_quotes() -> Dict:

    """
    Fixture to provide sample quotes for testing

    Returns:
    Dict: A dictionary containing sample quotes

    """
    return {
        "category1": [
            {"id": 1, "quote": "This is a test quote", "author": "Test Author"}
        ],
        "category2": [
            {
                "id": 2,
                "quote": "This is another test quote",
                "author": "Another Test Author",
            }
        ],
    }


@pytest.fixture
def runner() -> CliRunner:

    """
    Fixture to provide a CliRunner instance for testing

    Returns:
    CliRunner: A CliRunner instance

    """
    return CliRunner()


def string_to_dict(result_output: str) -> dict:

    """
    Function to convert a string to a dictionary

    Args:
    result_output (str): The string to convert

    Returns:
    Dict: The converted dictionary

    """

    try:
        result_dict = ast.literal_eval(result_output)
    except (ValueError, SyntaxError):
        try:
            result_dict = json.loads(result_output.replace("'", '"'))
        except json.JSONDecodeError:
            print("Unable to parse the string into a dictionary.")
            result_dict = {}
    return result_dict


@patch("src.cli.load_data")
@patch("src.cli.query_existing_data")
@patch("src.cli.get_db")
def test_import_quotes(
    mock_get_db: MagicMock,
    mock_query_existing_data: MagicMock,
    mock_load_data: MagicMock,
    runner: CliRunner,
    tmp_path: Path,
    sample_quotes: Dict[str, List],
) -> None:

    """
    Tests the import_quotes command

    Args:
    mock_get_db (MagicMock): A mock of the get_db function
    mock_query_existing_data (MagicMock): A mock of the query_existing_data function
    mock_load_data (MagicMock): A mock of the load_data function
    runner (CliRunner): A CliRunner instance
    tmp_path (Path): A temporary path
    sample_quotes (Dict[str, Any]): A dictionary containing sample quotes

    Returns:
    None

    """
    # Create a temporary JSON file with sample quotes
    file_path = tmp_path / "test_quotes.json"
    with open(file_path, "w") as f:
        json.dump(sample_quotes, f)

    # Mock the return value of load_data
    mock_load_data.return_value = sample_quotes

    # Mock the return value of query_existing_data
    mock_query_existing_data.return_value = {
        "existing_ids": [],
        "record_list": [
            {
                "id": 1,
                "quote": "This is a test quote",
                "author": "Test Author",
                "category": "category1",
            }
        ],
    }

    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    # Run the import_quotes command
    result = runner.invoke(import_quotes, ["--file_path", str(file_path)])
    result_output = result.output
    result_output = result_output.strip()

    result_dict = string_to_dict(result_output)

    # Check if the command executed successfully
    assert result.exit_code == 0, f"Command failed with error: {result.exception}"

    # Check if the expected output is in the result
    assert result_dict["status"] == "success"
    print("result_dict:", result_dict["message"])
    assert result_dict["message"] == f"1 data imported to database from {file_path}"

    # Verify that the session methods were called
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

    # Verify that the correct Quote object was added
    added_quote = mock_session.add.call_args[0][0]
    assert isinstance(added_quote, Quote)
    assert added_quote.id == 1
    assert added_quote.quote == "This is a test quote"
    assert added_quote.author == "Test Author"
    assert added_quote.category == "category1"


@patch("src.cli.get_db")
@patch("src.cli.random.choice")
def test_generate_without_category(
    mock_random_choice: MagicMock,
    mock_get_db: MagicMock,
    runner: CliRunner,
    sample_quotes: Dict[str, List],
) -> None:

    """
    Tests the generate command without a category

    Args:
    mock_random_choice (MagicMock): A mock of the random.choice function
    mock_get_db (MagicMock): A mock of the get_db function
    runner (CliRunner): A CliRunner instance
    sample_quotes (Dict[str, List]): A dictionary containing sample quotes

    Returns:
    None

    """
    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    # Set up the mock query
    mock_session.query.return_value.all.return_value = sample_quotes
    random_quote_dict = {
        list(sample_quotes.keys())[0]: sample_quotes[list(sample_quotes.keys())[0]]
    }

    # Set up the random choice
    sample_quotes_key = list(random_quote_dict.keys())[0]
    mock_random_choice.return_value = {
        "quote": random_quote_dict[sample_quotes_key][0]["quote"],
        "author": random_quote_dict[sample_quotes_key][0]["author"],
        "category": sample_quotes_key,
    }

    mock_random_choice_dict = mock_random_choice.return_value
    mock_random_choice_category = mock_random_choice_dict.get("category")
    mock_random_choice_quote = mock_random_choice_dict.get("quote")
    mock_random_choice_author = mock_random_choice_dict.get("author")

    # Run the generate command
    result = runner.invoke(generate)

    # Check the result
    assert result.exit_code == 0
    test_output = (
        f"{{'status': 'success', 'quote': '{mock_random_choice_quote}', "
        f"'category': '{mock_random_choice_category}', "
        f"'author': '{mock_random_choice_author}'}}"
    )
    assert test_output in result.output


@patch("src.cli.get_db")
@patch("src.cli.random.choice")
def test_generate_with_category(
    mock_random_choice: MagicMock,
    mock_get_db: MagicMock,
    runner: CliRunner,
    sample_quotes: Dict[str, List],
) -> None:

    """
    Tests the generate command with a category

    Args:
    mock_random_choice (MagicMock): A mock of the random.choice function
    mock_get_db (MagicMock): A mock of the get_db function
    runner (CliRunner): A CliRunner instance
    sample_quotes (Dict[str, List]): A dictionary containing sample quotes

    Returns:
    None

    """
    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    # initiate category
    category = "category1"

    # Set up the mock query
    mock_all_categories = [(category,) for category in sample_quotes.keys()]
    print("mock_all_categories:", mock_all_categories)
    mock_session.query.return_value.distinct.return_value.all.return_value = (
        mock_all_categories
    )

    # Set up the random choice
    category_filtered_quotes = sample_quotes.get(category)
    mock_random_choice.return_value = {
        "quote": category_filtered_quotes[0]["quote"],
        "author": category_filtered_quotes[0]["author"],
        "category": category,
    }

    mock_random_choice_dict = mock_random_choice.return_value
    mock_random_choice_category = mock_random_choice_dict.get("category")
    mock_random_choice_quote = mock_random_choice_dict.get("quote")
    mock_random_choice_author = mock_random_choice_dict.get("author")

    # Run the generate command with a category
    result = runner.invoke(generate, ["--category", category])

    # Check the result
    assert result.exit_code == 0
    test_output = (
        f"{{'status': 'success', 'quote': '{mock_random_choice_quote}', "
        f"'category': '{mock_random_choice_category}', "
        f"'author': '{mock_random_choice_author}'}}"
    )

    assert test_output in result.output


@patch("src.cli.get_db")
def test_generate_non_existent_category(
    mock_get_db: MagicMock, runner: CliRunner
) -> None:

    """
    Tests the generate command with a non-existent category

    Args:
    mock_get_db (MagicMock): A mock of the get_db function
    runner (CliRunner): A CliRunner instance

    Returns:
    None

    """
    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    # initiate category
    category = "non-existent"

    # Set up the mock query to return all categories
    mock_session.query.return_value.distinct.return_value.all.return_value = [
        ("Non-existent1",),
        ("Non-existent2",),
    ]

    # Run the generate command with a non-existent category
    result = runner.invoke(generate, ["--category", category])
    result_output = result.output
    result_output = result_output.strip()
    result_output = result_output[: result_output.find("}") + 1]
    result_dict = string_to_dict(result_output)

    # Check the result
    assert result.exit_code == 0
    assert result_dict["status"] == "error"
    assert (
        result_dict["message"]
        == f"quotes for category:[{category}] are not found in the database"
    )


@patch("src.cli.get_db")
def test_generate_no_quotes(mock_get_db: MagicMock, runner: CliRunner) -> None:

    """
    Tests the generate command when no quotes are found in the database

    Args:
    mock_get_db (MagicMock): A mock of the get_db function
    runner (CliRunner): A CliRunner instance

    Returns:
    None

    """
    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    # Set up the mock query to return no quotes
    mock_session.query.return_value.all.return_value = []

    # Run the generate command
    result = runner.invoke(generate)
    print("Output:", result.output)
    result_output = result.output
    result_output = result_output.strip()
    result_dict = string_to_dict(result_output)

    # Check the result
    assert result.exit_code == 0
    assert result_dict["status"] == "error"
    assert result_dict["message"] == "No quotes could be generated"


@patch("src.cli.get_db")
@patch("src.cli.error_logger")
def test_generate_database_error(
    mock_error_logger: MagicMock, mock_get_db: MagicMock, runner: CliRunner
) -> None:

    """
    Tests the generate command when a database error occurs

    Args:
    mock_error_logger (MagicMock): A mock of the error_logger function
    mock_get_db (MagicMock): A mock of the get_db function
    runner (CliRunner): A CliRunner instance

    Returns:
    None

    """
    # Mock the database session to raise an exception
    mock_get_db.side_effect = Exception("Database error")

    # Run the generate command
    result = runner.invoke(generate)

    result_output = result.output
    result_output = result_output.strip()
    result_dict = string_to_dict(result_output)

    # Check the result
    assert result.exit_code == 0
    assert result_dict["status"] == "error"
    assert (
        result_dict["message"]
        == "Error occurred during database operation: Database error"
    )
    mock_error_logger.error.assert_called_once_with(
        {
            "status": "error",
            "message": "Error occurred during database operation: Database error",
        }
    )


@patch("src.cli.get_db")
def test_add_with_all_parameters(mock_get_db: MagicMock, runner: CliRunner) -> None:

    """
    Test the add command provided with all parameters are provided

    Args:
    mock_get_db (MagicMock): A mock of the get_db function
    runner (CliRunner): A CliRunner instance

    Returns:
    None

    """
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    # set up test data
    category = "test category"
    quote = "this is a test quote"
    author = "test author"

    # run the add command
    result = runner.invoke(
        add, ["--category", category, "--quote", quote, "--author", author]
    )
    result_output = result.output
    result_output = result_output.strip()
    result_dict = string_to_dict(result_output)

    # check the result
    assert result.exit_code == 0
    assert result_dict["status"] == "success, quote added successfully"
    assert result_dict["quote"] == quote
    assert result_dict["category"] == category
    assert result_dict["author"] == author

    # Verify that the quote was added to the database
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@patch("src.cli.get_db")
def test_add_missing_required_parameters(
    mock_get_db: MagicMock, runner: CliRunner
) -> None:

    """
    Tests the add command with missing required parameters

    Args:
    mock_get_db (MagicMock): A mock of the get_db function
    runner (CliRunner): A CliRunner instance

    Returns:
    None

    """
    # Run the add command without required parameters
    result = runner.invoke(add)

    # Check the result
    assert result.exit_code != 0
    assert "Missing option" in result.output


@patch("src.cli.get_db")
@patch("src.cli.error_logger")
def test_add_database_error(
    mock_error_logger: MagicMock, mock_get_db: MagicMock, runner: CliRunner
) -> None:

    """
    Tests the add command when a database error occurs

    Args:
    mock_error_logger (MagicMock): A mock of the error_logger function
    mock_get_db (MagicMock): A mock of the get_db function

    Returns:
    None

    """
    # Mock the database session to raise an exception
    mock_get_db.side_effect = Exception("Database error")

    # Set up test data
    category = "test category"
    quote = "this is a test quote"
    author = "test author"

    # Run the add command
    result = runner.invoke(
        add, ["--category", category, "--quote", quote, "--author", author]
    )
    result_output = result.output
    result_output = result_output.strip()
    result_dict = string_to_dict(result_output)

    # Check the result
    assert result.exit_code == 0
    assert result_dict["status"] == "error"
    assert (
        result_dict["message"]
        == "Error occurred during database operation: Database error"
    )
    mock_error_logger.error.assert_called_once_with(
        {
            "status": "error",
            "message": "Error occurred during database operation: Database error",
        }
    )


@patch("src.cli.get_db")
@patch("random.choices")
def test_list_without_category(
    mock_random_choices: MagicMock, mock_get_db: MagicMock, runner: CliRunner
) -> None:

    """
    Tests the list command without a category

    Args:
    mock_random_choices (MagicMock): A mock of the random.choices function
    mock_get_db (MagicMock): A mock of the get_db function
    runner (CliRunner): A CliRunner instance

    Returns:
    None

    """
    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    # Set up mock quotes
    mock_quotes = [
        Quote(quote="Quote 1", author="Author 1", category="Category 1"),
        Quote(quote="Quote 2", author="Author 2", category="Category 2"),
        Quote(quote="Quote 3", author="Author 3", category="Category 3"),
        Quote(quote="Quote 4", author="Author 4", category="Category 4"),
        Quote(quote="Quote 5", author="Author 5", category="Category 5"),
    ]
    mock_session.query.return_value.all.return_value = mock_quotes
    mock_random_choices.return_value = mock_quotes

    # Run the list command
    result = runner.invoke(list_quotes)

    # Check the result
    assert result.exit_code == 0
    for quote in mock_quotes:
        assert quote.quote in result.output
        assert quote.author in result.output
        assert quote.category in result.output


@patch("src.cli.get_db")
@patch("random.choices")
def test_list_with_category(
    mock_random_choices: MagicMock, mock_get_db: MagicMock, runner: CliRunner
) -> None:

    """
    Tests the list command with a category

    Args:
    mock_random_choices (MagicMock): A mock of the random.choices function
    mock_get_db (MagicMock): A mock of the get_db function
    runner (CliRunner): A CliRunner instance

    Returns:
    None

    """
    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    # Set up mock quotes
    category = "test category"
    mock_quotes = [
        Quote(quote="Quote 1", author="Author 1", category=category),
        Quote(quote="Quote 2", author="Author 2", category=category),
        Quote(quote="Quote 3", author="Author 3", category=category),
        Quote(quote="Quote 4", author="Author 4", category=category),
        Quote(quote="Quote 5", author="Author 5", category=category),
    ]
    mock_session.query.return_value.filter.return_value.all.return_value = mock_quotes
    mock_random_choices.return_value = mock_quotes

    # Run the list command
    result = runner.invoke(list_quotes, ["--category", category])

    # Check the result
    assert result.exit_code == 0
    for quote in mock_quotes:
        assert quote.quote in result.output
        assert quote.author in result.output
        assert category in result.output


@patch("src.cli.get_db")
@patch("random.choices")
def test_list_no_quotes(
    mock_random_choices: MagicMock, mock_get_db: MagicMock, runner: CliRunner
) -> None:

    """
    Tests the list command when no quotes are found

    Args:
    mock_random_choices (MagicMock): A mock of the random.choices function
    mock_get_db (MagicMock): A mock of the get_db function
    runner (CliRunner): A CliRunner instance

    Returns:
    None

    """
    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    # Set up mock to return no quotes
    mock_quotes = []
    mock_session.query.return_value.all.return_value = mock_quotes
    mock_random_choices.return_value = mock_quotes

    # Run the list command
    result = runner.invoke(list_quotes)
    result_output = result.output
    result_output = result_output.strip()
    result_dict = string_to_dict(result_output)

    # Check the result
    assert result.exit_code == 0
    assert result_dict["status"] == "error"
    assert result_dict["message"] == "No quotes could be retrieved in the database"


@patch("src.cli.get_db")
@patch("src.cli.error_logger")
def test_list_database_error(
    mock_error_logger: MagicMock, mock_get_db: MagicMock, runner: CliRunner
) -> None:

    """
    Tests the list command when a database error occurs

    Args:
    mock_error_logger (MagicMock): A mock of the error_logger function
    mock_get_db (MagicMock): A mock of the get_db function
    runner (CliRunner): A CliRunner instance

    Returns:
    None

    """

    # Mock the database session to raise an exception
    mock_get_db.side_effect = Exception("Database error")

    # Run the list command
    result = runner.invoke(list_quotes)
    result_output = result.output
    result_output = result_output.strip()
    result_dict = string_to_dict(result_output)

    # Check the result
    assert result.exit_code == 0
    assert result_dict["status"] == "error"
    assert (
        result_dict["message"]
        == "Error occurred during database operation: Database error"
    )
    mock_error_logger.error.assert_called_once_with(
        {
            "status": "error",
            "message": "Error occurred during database operation: Database error",
        }
    )
