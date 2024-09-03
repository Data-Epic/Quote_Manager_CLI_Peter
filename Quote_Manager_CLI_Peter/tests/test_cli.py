import pytest
import os
import json
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from src.cli import import_quotes, generate, create_log_file, add, list_quotes
from src.models import Quote
import random

@pytest.fixture
def sample_quotes():
    return {
        "category1": [
            {
                "id": 1,
                "quote": "This is a test quote",
                "author": "Test Author"
            }
        ],
        "category2": [
            {
                "id": 2,
                "quote": "This is another test quote",
                "author": "Another Test Author"
            }
        ]
    }

@pytest.fixture
def runner():
    return CliRunner()

#create a log directory for the tests
curr_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(curr_dir)
print("base_dir", base_dir)
var_dir = os.path.join(base_dir, "var")

if not os.path.exists(var_dir):
    os.makedirs(var_dir)


def test_create_log_file():
    """Test to create a log file with valid input arguments"""

    log_file_name = "test.log"
    error_log_file_name = "test_error.log"
    
    log_file_path, error_log_file_path = create_log_file(log_file_name, error_log_file_name, var_dir)

    assert os.path.exists(log_file_path)
    assert os.path.exists(error_log_file_path)

def test_create_log_file_invalid_file_format():
    """Test to create a log file with invalid file format"""

    log_file_name = "test.txt"
    error_log_file_name = "test_error.txt"

    with pytest.raises(ValueError) as e:
        create_log_file(log_file_name, error_log_file_name, var_dir)
    
    assert str(e.value) == "Invalid file format. Only log files are allowed"

def test_create_log_file_invalid_input_arguments():
    """Test to create a log file with invalid input arguments"""

    log_file_name = 123
    error_log_file_name = 123

    with pytest.raises(ValueError) as e:
        create_log_file(log_file_name, error_log_file_name, var_dir)
    
    assert str(e.value) == "Invalid input arguments. Input arguments must be strings"


@patch('src.cli.load_data')
@patch('src.cli.query_existing_data')
@patch('src.cli.get_db')
def test_import_quotes(mock_get_db, mock_query_existing_data, mock_load_data, runner, 
                       tmp_path, sample_quotes):
    """
    Tests the import_quotes command
    """
    # Create a temporary JSON file with sample quotes
    file_path = tmp_path / "test_quotes.json"
    with open(file_path, 'w') as f:
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
                "category": "category1"
            }
        ]
    }

    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    # Run the import_quotes command
    result = runner.invoke(import_quotes, ['--file_path', str(file_path)])
    
    print("Output:", result.output)
    print("Exit code:", result.exit_code)
    
    # Check if the command executed successfully
    assert result.exit_code == 0, f"Command failed with error: {result.exception}"
    
    # Check if the expected output is in the result
    assert f"1 data imported to database successfully from {file_path}" in result.output

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


@patch('src.cli.get_db')
@patch('src.cli.random.choice')
def test_generate_without_category(mock_random_choice, mock_get_db, runner, sample_quotes):
    """
    Tests the generate command without a category
    """
    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    # Set up the mock query
    mock_session.query.return_value.all.return_value = sample_quotes


    sample_items = sample_quotes.items()
    print("sample_items", sample_items)
    list_items = list(sample_items)
    print("list_items", list_items)

    random_quote = random.choice(list_items)
    print("random_quote", random_quote)
    random_quote_dict = {list(sample_quotes.keys())[0]: sample_quotes[list(sample_quotes.keys())[0]]}

    # Set up the random choice
    sample_quotes_key = list(random_quote_dict.keys())[0]
    mock_random_choice.return_value = {
        "quote": random_quote_dict[sample_quotes_key][0]["quote"],
        "author": random_quote_dict[sample_quotes_key][0]["author"],
        "category": sample_quotes_key
    }

    mock_random_choice_dict = mock_random_choice.return_value
    mock_random_choice_category = mock_random_choice_dict.get("category")
    mock_random_choice_quote = mock_random_choice_dict.get("quote")
    mock_random_choice_author = mock_random_choice_dict.get("author")

    print("mock_random_choice_dict:", mock_random_choice_dict)

    # Run the generate command
    result = runner.invoke(generate)

    print("Output:", result.output)

    # Check the result
    assert result.exit_code == 0
    test_output = f"{{'status': 'success', 'quote': '{mock_random_choice_quote}', 'category': '{mock_random_choice_category}', 'author': '{mock_random_choice_author}'}}"
    assert test_output in result.output


@patch('src.cli.get_db')
@patch('src.cli.random.choice')
def test_generate_with_category(mock_random_choice, mock_get_db, runner, sample_quotes):
    """
    Tests the generate command with a category
    """
    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    #initiate category
    category = "category1"

    # Set up the mock query
    mock_all_categories = [(category, ) for category in sample_quotes.keys()]
    print("mock_all_categories:", mock_all_categories)
    # mock_session.query.return_value.filter.return_value.all.return_value = mock_all_categories
    mock_session.query.return_value.distinct.return_value.all.return_value = mock_all_categories

    # Set up the random choice
    category_filtered_quotes = sample_quotes.get(category)
    print("category_filtered_quotes:", category_filtered_quotes)

    mock_random_choice.return_value = {
        "quote": category_filtered_quotes[0]["quote"],
        "author": category_filtered_quotes[0]["author"],
        "category": category
    }

    mock_random_choice_dict = mock_random_choice.return_value
    mock_random_choice_category = mock_random_choice_dict.get("category")
    mock_random_choice_quote = mock_random_choice_dict.get("quote")
    mock_random_choice_author = mock_random_choice_dict.get("author")

    # Run the generate command with a category
    result = runner.invoke(generate, ['--category', category])

    print("Output:", result.output)

    # Check the result
    assert result.exit_code == 0
    test_output = f"{{'status': 'success', 'quote': '{mock_random_choice_quote}', 'category': '{mock_random_choice_category}', 'author': '{mock_random_choice_author}'}}"
    assert test_output in result.output

@patch('src.cli.get_db')
def test_generate_non_existent_category(mock_get_db, runner):
    """
    Tests the generate command with a non-existent category
    """
    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    #initiate category
    category = "Non-existent"

    # Set up the mock query to return all categories
    mock_session.query.return_value.distinct.return_value.all.return_value = [("Non-existent1",), ("Non-existent2",)]

    # Run the generate command with a non-existent category
    result = runner.invoke(generate, ['--category', category])
    print("Output:", result.output)

    # Check the result
    assert result.exit_code == 0
    test_output = f"{{'status': 'error', 'message': '{category} is not found in the database'}}"
    assert test_output in result.output

@patch('src.cli.get_db')
def test_generate_no_quotes(mock_get_db, runner):
    """
    Tests the generate command when no quotes are found in the database
    """
    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    # Set up the mock query to return no quotes
    mock_session.query.return_value.all.return_value = []

    # Run the generate command
    result = runner.invoke(generate)

    # Check the result
    assert result.exit_code == 0
    assert "No quotes found." in result.output

@patch('src.cli.get_db')
@patch('src.cli.error_logger')
def test_generate_database_error(mock_error_logger, mock_get_db, runner):
    """
    Tests the generate command when a database error occurs
    """
    # Mock the database session to raise an exception
    mock_get_db.side_effect = Exception("Database error")

    # Run the generate command
    result = runner.invoke(generate)

    # Check the result
    assert result.exit_code == 0
    assert "Error occurred during database operation: Database error" in result.output
    mock_error_logger.error.assert_called_once_with("Error occurred during database operation: Database error")


@patch('src.cli.get_db')
def test_add_with_all_parameters(mock_get_db, runner):
    """
    Test the add command provided with all parameters are provided 

    """
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    #set up test data
    category = "Test Category"
    quote = "This is a test quote"
    author = "Test Author"

    #run the add command
    result = runner.invoke(add, ['--category', category, '--quote', quote, '--author', author])

    print("result", result.output)

    #check the result
    assert result.exit_code == 0
    assert "success, quote added successfully" in result.output
    assert quote in result.output
    assert category in result.output
    assert author in result.output

    # Verify that the quote was added to the database
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

@patch('src.cli.get_db')
def test_add_without_author(mock_get_db, runner):
    """
    Tests the add command without an author
    """
    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    # Set up test data
    category = "Test Category"
    quote = "This is a test quote"

    # Run the add command
    result = runner.invoke(add, ['--category', category, '--quote', quote])

    # Check the result
    assert result.exit_code == 0
    assert "success, quote added successfully" in result.output
    assert quote in result.output
    assert category in result.output
    assert "None" in result.output  # Author should be None

    # Verify that the quote was added to the database
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

@patch('src.cli.get_db')
def test_add_missing_required_parameters(mock_get_db, runner):
    """
    Tests the add command with missing required parameters
    """
    # Run the add command without required parameters
    result = runner.invoke(add)

    # Check the result
    assert result.exit_code != 0
    assert "Missing option" in result.output

@patch('src.cli.get_db')
@patch('src.cli.error_logger')
def test_add_database_error(mock_error_logger, mock_get_db, runner):
    """
    Tests the add command when a database error occurs
    """
    # Mock the database session to raise an exception
    mock_get_db.side_effect = Exception("Database error")

    # Set up test data
    category = "Test Category"
    quote = "This is a test quote"

    # Run the add command
    result = runner.invoke(add, ['--category', category, '--quote', quote])

    # Check the result
    assert result.exit_code == 0
    assert "Error occurred during database operation: Database error" in result.output
    mock_error_logger.error.assert_called_once_with("Error occurred during database operation: Database error")

@patch('src.cli.get_db')
@patch('random.choices')
def test_list_without_category(mock_random_choices, mock_get_db, runner):
    """
    Tests the list command without a category
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
    print("result", result.output)
    
    # Check the result
    assert result.exit_code == 0
    for quote in mock_quotes:
        assert quote.quote in result.output
        assert quote.author in result.output
        assert quote.category in result.output

@patch('src.cli.get_db')
@patch('random.choices')
def test_list_with_category(mock_random_choices, mock_get_db, runner):
    """
    Tests the list command with a category

    """
    # Mock the database session
    mock_session = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_session
    mock_get_db.return_value.__exit__.return_value = None

    # Set up mock quotes
    category = "Test Category"
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
    result = runner.invoke(list_quotes, ['--category', category])

    # Check the result
    assert result.exit_code == 0
    for quote in mock_quotes:
        assert quote.quote in result.output
        assert quote.author in result.output
        assert category in result.output

@patch('src.cli.get_db')
@patch('random.choices')
def test_list_no_quotes(mock_random_choices,mock_get_db, runner):
    """
    Tests the list command when no quotes are found
    
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

    print("result_output", result.output)

    # Check the result
    assert result.exit_code == 0
    assert "No quotes found." in result.output

@patch('src.cli.get_db')
@patch('src.cli.error_logger')
def test_list_database_error(mock_error_logger, mock_get_db, runner):
    """
    Tests the list command when a database error occurs
    """
    # Mock the database session to raise an exception
    mock_get_db.side_effect = Exception("Database error")

    # Run the list command
    result = runner.invoke(list_quotes)

    # Check the result
    assert result.exit_code == 0
    assert "Error occurred during database operation: Database error" in result.output
    mock_error_logger.error.assert_called_once_with("Error occurred during database operation: Database error")


    


 
