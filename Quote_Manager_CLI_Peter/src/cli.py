import logging
import random
from typing import Optional

import click
from src.database import get_db
from src.logger_config import error_log_file_path, log_file_path
from src.models import Quote
from src.utils import load_data, query_existing_data

# set up logging
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler(error_log_file_path)
error_logger.addHandler(error_handler)

logger_handler = logging.FileHandler(log_file_path)
logger = logging.getLogger("logger")
logger.addHandler(logger_handler)


@click.group()
def cli():

    pass


@cli.command()
@click.option(
    "--file_path",
    default="data/quotes.json",
    help="Path to the json file containing quotes",
)
def import_quotes(file_path: str) -> None:
    """
    Import quotes from a json file to the database

    Args:
    file_path (str): Path to the json file containing quotes

    Returns:
    None
    """
    try:

        with get_db() as db:

            data = load_data(file_path)

            data = query_existing_data(Quote, data, db)
            existing_ids = data["existing_ids"]
            record_list = data["record_list"]

            no_data = 0
            for record in record_list:

                if record["id"] not in existing_ids:

                    record = Quote(
                        category=record["category"],
                        id=record["id"],
                        author=record["author"],
                        quote=record["quote"],
                    )
                    db.add(record)
                    no_data += 1
            db.commit()
            click.echo(
                {
                    "status": "success",
                    "message": f"{no_data} data imported to database from {file_path}",
                }
            )
            logger.info(
                {
                    "status": "success",
                    "message": f"{no_data} data imported to database from {file_path}",
                }
            )

    except Exception as e:
        click.echo(
            {
                "status": "error",
                "message": f"Error occurred during \
                database operation: {str(e)}",
            }
        )
        error_logger.error(
            {
                "status": "error",
                "message": f"Error occurred during database operation: {str(e)}",
            }
        )


@cli.command()
@click.option("--category", default=None, help="Category of the quote")
@click.option("--author", default=None, help="Author of the quote")
def generate(category: Optional[str], author: Optional[str]) -> None:
    """
    Generates a random quote from the database
    by passing a category

    Args:
    category (Optional[str]): Category of the quote. Defaults to None.
    author (Optional[str]): Author of the quote. Defaults to None.

    Returns:
    None

    """
    try:

        with get_db() as db:

            if category and author:

                category = category.lower()
                author = author.lower()

                all_categories = db.query(Quote.category).distinct().all()
                all_categories = [category[0] for category in all_categories]

                all_authors = db.query(Quote.author).distinct().all()
                all_authors = [author[0] for author in all_authors]

                if category not in all_categories or author not in all_authors:

                    click.echo(
                        {
                            "status": "error",
                            "message": f"quotes for category:[{category}] and author:[{author}] are not found in the database",
                        }
                    )
                    error_logger.error(
                        {
                            "status": "error",
                            "message": f"quotes for category:[{category}] and author:[{author}] are not found in the database",
                        }
                    )

                quotes = (
                    db.query(Quote)
                    .filter(Quote.category == category, Quote.author == author)
                    .all()
                )

            elif category:

                category = category.lower()

                all_categories = db.query(Quote.category).distinct().all()
                all_categories = [category[0] for category in all_categories]

                if category not in all_categories:

                    click.echo(
                        {
                            "status": "error",
                            "message": f"quotes for category:[{category}] are not found in the database",
                        }
                    )
                    error_logger.error(
                        {
                            "status": "error",
                            "message": f"quotes for category:[{category}] are not found in the database",
                        }
                    )
                quotes = db.query(Quote).filter(Quote.category == category).all()

            elif author:

                author = author.lower()
                all_authors = db.query(Quote.author).distinct().all()
                all_authors = [author[0] for author in all_authors]

                if author not in all_authors:

                    click.echo(
                        {
                            "status": "error",
                            "message": f"quotes by author:[{author}] are not found in the database",
                        }
                    )
                    error_logger.error(
                        {
                            "status": "error",
                            "message": f"quotes by author:[{author}] are not found in the database",
                        }
                    )

                quotes = db.query(Quote).filter(Quote.author == author).all()

            else:
                quotes = db.query(Quote).all()

            if quotes:

                quote = random.choice(quotes)

                if isinstance(quote, Quote):

                    quote = quote.__dict__

                elif isinstance(quote, dict):

                    quote = quote

                else:

                    raise ValueError("Invalid quote format")

                click.echo(
                    {
                        "status": "success",
                        "quote": quote.get("quote"),
                        "category": quote.get("category"),
                        "author": quote.get("author"),
                    }
                )
                logger.info(
                    {
                        "status": "success",
                        "quote": quote.get("quote"),
                        "category": quote.get("category"),
                        "author": quote.get("author"),
                    }
                )
            else:
                click.echo(
                    {"status": "error", "message": "No quotes could be generated"}
                )
                error_logger.error(
                    {"status": "error", "message": "No quotes could be generated"}
                )

    except Exception as e:

        click.echo(
            {
                "status": "error",
                "message": f"Error occurred during database operation: {str(e)}",
            }
        )
        error_logger.error(
            {
                "status": "error",
                "message": f"Error occurred during database operation: {str(e)}",
            }
        )


@cli.command()
@click.option("--category", required=True, help="Category of the quote")
@click.option("--quote", required=True, help="The quote to be added")
@click.option("--author", required=True, help="The author of the quote")
def add(category: str, quote: str, author: str) -> None:
    """
    Adds a new quote to the database if the quote,
    category, and author are provided

    Args:
    category (str): category of the quote
    quote (str): The quote to be added
    author (str): The author of the quote

    Returns:
    None

    """
    try:

        with get_db() as db:

            if quote and category and author:

                quote = quote.lower()
                category = category.lower()
                author = author.lower()
                new_quote = Quote(category=category, quote=quote, author=author)
                db.add(new_quote)
                db.commit()

                click.echo(
                    {
                        "status": "success, quote added successfully",
                        "quote": quote,
                        "category": category,
                        "author": author,
                    }
                )

                logger.info(
                    {
                        "status": "success, quote added successfully",
                        "quote": quote,
                        "category": category,
                        "author": author,
                    }
                )

            else:

                click.echo(
                    {
                        "status": "error",
                        "message": "Please provide the required \
                    arguments: quote, category and author",
                    }
                )
                error_logger.error(
                    {
                        "status": "error",
                        "message": "Please provide the required \
                    arguments: quote, category and author",
                    }
                )

    except Exception as e:

        click.echo(
            {
                "status": "error",
                "message": f"Error occurred during database operation: {str(e)}",
            }
        )
        error_logger.error(
            {
                "status": "error",
                "message": f"Error occurred during database operation: {str(e)}",
            }
        )


@cli.command()
@click.option("--category", default=None, help="Category of the quote")
@click.option("--author", default=None, help="Author of the quote")
def list_quotes(category: Optional[str], author: Optional[str]) -> None:
    """
    Lists 5 random quotes in the database if no
    category or author is provided, else,
    it lists 5 random quotes in the category or author provided

    Args:
    category (Optional[str]): Category of the quote
    author (Optional[str]): Author of the quote

    Returns:
    None

    """
    try:

        with get_db() as db:

            if category and author is None:

                category = category.lower()
                quotes = db.query(Quote).filter(Quote.category == category).all()
                quotes = random.choices(quotes, k=5)

            elif author and category is None:

                author = author.lower()
                quotes = db.query(Quote).filter(Quote.author == author).all()
                quotes = random.choices(quotes, k=5)

            elif category and author:

                category = category.lower()
                author = author.lower()
                quotes = (
                    db.query(Quote)
                    .filter(Quote.category == category, Quote.author == author)
                    .all()
                )
                quotes = random.choices(quotes, k=5)

            else:

                quotes = db.query(Quote).all()
                quotes = random.choices(quotes, k=5)

            if quotes:

                quotes_list = []

                for quote in quotes:

                    quote = quote.__dict__
                    quotes_list.append(
                        {
                            "quote": quote.get("quote"),
                            "category": quote.get("category"),
                            "author": quote.get("author"),
                        }
                    )

                click.echo(
                    {
                        "status": "success",
                        "message": "quotes listed successfully",
                        "quotes": quotes_list,
                    }
                )

                for quote in quotes_list:

                    logger.info(
                        {
                            "status": "success",
                            "message": "quote listed successfully",
                            "quotes": quote,
                        }
                    )

            else:

                click.echo(
                    {
                        "status": "error",
                        "message": "No quotes could be retrieved in the database",
                    }
                )
                error_logger.error(
                    {
                        "status": "error",
                        "message": "No quotes could be retrieved in the database",
                    }
                )

    except Exception as e:

        click.echo(
            {
                "status": "error",
                "message": f"Error occurred during database operation: {str(e)}",
            }
        )
        error_logger.error(
            {
                "status": "error",
                "message": f"Error occurred during database operation: {str(e)}",
            }
        )


@cli.command()
def list_categories() -> None:
    """
    Lists all quotes in the category provided

    Returns:
    None

    """

    try:

        with get_db() as db:

            categories = db.query(Quote.category).distinct().all()
            all_categories = [category[0] for category in categories]

            click.echo(
                {
                    "status": "success",
                    "message": "categories listed successfully",
                    "categories": all_categories,
                }
            )

            logger.info(
                {
                    "status": "success",
                    "message": "category listed successfully",
                    "categories": all_categories,
                }
            )

    except Exception as e:

        click.echo(
            {
                "status": "error",
                "message": f"Error occurred during database operation: {str(e)}",
            }
        )
        error_logger.error(
            {
                "status": "error",
                "message": f"Error occurred during database operation: {str(e)}",
            }
        )


@cli.command()
def list_authors() -> None:
    """
    Lists all authors in the database

    Returns:
    None

    """

    try:

        with get_db() as db:

            authors = db.query(Quote.author).distinct().all()
            all_authors = [author[0] for author in authors]

            click.echo(
                {
                    "status": "success",
                    "message": "authors listed successfully",
                    "authors": all_authors,
                }
            )

            logger.info(
                {
                    "status": "success",
                    "message": "authors listed successfully",
                    "authors": all_authors,
                }
            )

    except Exception as e:
        click.echo(
            {
                "status": "error",
                "message": f"Error occurred during database operation: {str(e)}",
            }
        )
        error_logger.error(
            {
                "status": "error",
                "message": f"Error occurred during database operation: {str(e)}",
            }
        )


if __name__ == "main":
    cli()
