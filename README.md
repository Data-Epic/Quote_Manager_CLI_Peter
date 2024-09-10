# Quote_Manager_CLI_Peter

## Project Overview

Quote Manager is a command-line interface (CLI) tool designed to manage and interact with a collection of quotes. This tool demonstrates proficiency in Python CLI development, package management with Poetry, database integration, Linux system administration, unit testing, file operations, and code quality management.

## Features

- Import quotes from a JSON file into a database
- Generate random quotes, with optional category filtering
- Generate random quotes, with optional author filtering
- Add new quotes via the command line
- List quotes, with optional category and author filtering
- List all categories
- List all authors
- Logging functionality for both general logs and error logs
- Code quality checks with pre-commit hooks
- Continuous Integration with GitHub Actions

## Installation

### Prerequisites

- Python 3.7+
- Poetry
- SQLite (or your chosen database system)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/quote-manager.git
   cd Quote_Manager_CLI_Peter
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Activate the virtual environment:
   ```
   poetry shell
   ```

4. Set up pre-commit hooks:
   ```
   pre-commit install
   ```

## Usage

Here are the main commands available in the Quote Manager CLI:

1. Generate a random quote:

   ```
   poetry run quote generate
   ```

2. Generate a quote by category:

   ```
   poetry run quote generate --category "life"
   ```

3. Generate a quote by author:

   ```
   poetry run quote generate --author "Tom Clancy"
   ```

4. Add a new quote:

   ```
   poetry run quote add --category "Wisdom" --quote "Patience is a virtue." --author "Sogo"
   ```

5. List 5 quotes:

   ```
   poetry run quote list-quotes
   ```

6. List 5 quotes by category:

   ```
   poetry run quote list-quotes --category "Humor"
   ```

7. List 5 quotes by author:

   ```
   poetry run quote list-quotes --author "tom clancy"
   ```

8. List all categories:

   ```
   poetry run quote list-categories
   ```

9. List all authors:

   ```
   poetry run quote list-authors
   ```

## Project Structure

```
Quote_Manager_CLI_Peter/
│
├── pyproject.toml
├── poetry.lock
├── README.md
├── .pre-commit-config.yaml
├── .flake8
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── src/
│   ├── __init__.py
│   ├── cli.py
│   ├── logger_config.py
│   ├── models.py
│   ├── database.py
│   └── utils.py
│
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_database.py
│   ├── test_utils.py
│   └── test_logger_config.py
│
└── data/
    └── quotes.json
```

## Development

### Running Tests

To run the unit tests:

```
poetry run pytest
```

### Code Quality

This project uses pre-commit hooks to maintain code quality. The following checks are run:

- Trailing whitespace removal
- End-of-file fixing
- YAML syntax checking
- Large file detection
- Code formatting with Black
- Import sorting with isort
- Linting with flake8

To run the pre-commit checks manually:

```
poetry run pre-commit run --all-files
```

### Continuous Integration

This project uses GitHub Actions for continuous integration. The CI pipeline:

- Runs pre-commit hooks
- Runs the test suite

The workflow is defined in `.github/workflows/ci.yml`.

### Logging

Logs are generated in the following locations:
- General logs: `/var/log/quote_manager.log`
- Error logs: `/var/log/quote_manager-error.log`

Note: Ensure the application has write permissions to these locations.

## Acknowledgments

- Data source: [GitHub Readme Quotes](https://github.com/shravan20/github-readme-quotes/blob/main/customQuotes/category.json)
```
