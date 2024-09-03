# Quote_Manager_CLI_Peter

## Project Overview

Quote Manager is a command-line interface (CLI) tool designed to manage and interact with a collection of quotes. This tool demonstrates proficiency in Python CLI development, package management with Poetry, database integration, Linux system administration, unit testing, and file operations.

## Features

- Import quotes from a JSON file into a database
- Generate random quotes, with optional category filtering
- Add new quotes via the command line
- List quotes, with optional category filtering
- Logging functionality for both general logs and error logs

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

## Usage

Here are the main commands available in the Quote Manager CLI:

1. Generate a random quote:
   ```
   quote generate
   ```

2. Generate a quote by category:
   ```
   quote generate --category "life"
   ```

3. Add a new quote:
   ```
   quote add --category "Wisdom" --text "Patience is a virtue."
   ```

4. List 5 quotes:
   ```
   quote list
   ```

5. List 5 quotes by category:
   ```
   quote list --category "Humor"
   ```

## Project Structure

```
Quote_Manager_CLI_Peter/
│
├── pyproject.toml
├── README.md
├── setup_db.py
├── import_quotes.py
│
├── src/
│   ├── __init__.py
│   ├── cli.py
│   ├── models.py
│   ├── database.py
│   └── utils.py
│
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_models.py
│   └── test_utils.py
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

### Logging

Logs are generated in the following locations:
- General logs: `/var/log/quote_manager.log`
- Error logs: `/var/log/quote_manager-error.log`

Note: Ensure the application has write permissions to these locations.

## Acknowledgments

- Data source: [GitHub Readme Quotes](https://github.com/shravan20/github-readme-quotes/blob/main/customQuotes/category.json)
