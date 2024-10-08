from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from quote_manager_cli_peter.database import db_path, get_db
from quote_manager_cli_peter.models import Base, Quote

TEST_DB_PATH = "test_quotes.db"


@pytest.fixture(scope="module")
def test_db():

    """
    This function tests the database engine

    Yields:
    engine: A sqlalchemy engine object

    """
    test_engine = create_engine(f"sqlite:///{TEST_DB_PATH}")
    Base.metadata.create_all(test_engine)

    yield test_engine

    Base.metadata.drop_all(test_engine)


@pytest.fixture(scope="function")
def db_session(test_db: create_engine) -> Generator[Session, None, None]:

    """
    This function provides a session for the test database

    Args:
    test_db: A sqlalchemy engine object

    Yields:
    session: A sqlalchemy session object

    """
    with get_db() as session:
        yield session


def test_database_connection(db_session) -> None:

    """
    Test the database connection

    Returns: None

    """
    assert isinstance(db_session, Session)


def test_add_quote(db_session) -> None:

    """
    Test adding a quote to the database

    Returns: None

    """
    new_quote = Quote(
        quote="This is a test quote", author="Test Author", category="Test Category"
    )
    db_session.add(new_quote)
    db_session.commit()

    retrieved_quote = (
        db_session.query(Quote).filter(Quote.author == "Test Author").first()
    )
    assert retrieved_quote is not None
    assert retrieved_quote.quote == "This is a test quote"
    assert retrieved_quote.category == "Test Category"


def test_retrieve_quote(db_session) -> None:

    """
    Test retrieving a quote from the database

    Returns: None

    """
    new_quote = Quote(
        quote="This is a retrieved quote",
        author="Retrieved Peter",
        category="Retrieved Category",
    )
    db_session.add(new_quote)
    db_session.commit()

    retrieved_quote = (
        db_session.query(Quote).filter(Quote.author == "Retrieved Peter").first()
    )
    assert retrieved_quote is not None
    assert retrieved_quote.quote == "This is a retrieved quote"
    assert retrieved_quote.category == "Retrieved Category"


def test_update_quote(db_session) -> None:

    """
    Test updating a quote in the database

    Returns: None

    """
    new_quote = Quote(
        quote="This is an updated quote",
        author="Updated Peter",
        category="Updated Category",
    )
    db_session.add(new_quote)
    db_session.commit()

    retrieved_quote = (
        db_session.query(Quote).filter(Quote.author == "Updated Peter").first()
    )
    assert retrieved_quote is not None
    assert retrieved_quote.quote == "This is an updated quote"
    assert retrieved_quote.category == "Updated Category"

    retrieved_quote.quote = "This is the latest updated quote"
    db_session.commit()

    updated_quote = (
        db_session.query(Quote).filter(Quote.author == "Updated Peter").first()
    )
    assert updated_quote is not None
    assert updated_quote.quote == "This is the latest updated quote"
    assert updated_quote.category == "Updated Category"


def test_delete_quote(db_session) -> None:

    """
    Test deleting a quote from the database

    Returns: None

    """
    new_quote = Quote(
        quote="This is a deleted quote",
        author="Deleted Peter",
        category="Deleted Category",
    )
    db_session.add(new_quote)
    db_session.commit()

    retrieved_quote = (
        db_session.query(Quote).filter(Quote.author == "Deleted Peter").first()
    )
    assert retrieved_quote is not None
    assert retrieved_quote.quote == "This is a deleted quote"
    assert retrieved_quote.category == "Deleted Category"

    db_session.delete(retrieved_quote)
    db_session.commit()

    deleted_quote = (
        db_session.query(Quote).filter(Quote.author == "Deleted Peter").first()
    )
    assert deleted_quote is None


def test_db_context_manager() -> None:

    """
    Test the database context manager (get_db)

    Returns: None

    """
    with get_db() as db:
        assert isinstance(db, Session)
        assert db.bind.url.database == db_path


def test_db_context_manager_error() -> None:

    """
    Test the database context manager (get_db) with an error

    Returns: None

    """
    with pytest.raises(Exception):
        with get_db() as db:
            assert isinstance(db, Session)
            assert db.bind.url.database == db_path
            raise Exception("An error occurred")


def test_multiple_quotes(db_session) -> None:

    """
    Test adding multiple quotes to the database

    Returns: None

    """
    multiple_quotes = [
        Quote(
            quote="This is a test quote by Peter",
            author="Peter1",
            category="multiple_quote",
        ),
        Quote(
            quote="This is a test quote by Peter",
            author="Peter2",
            category="multiple_quote",
        ),
        Quote(
            quote="This is a test quote by Peter",
            author="Peter3",
            category="multiple_quote",
        ),
    ]
    db_session.add_all(multiple_quotes)
    db_session.commit()

    retrieved_quotes = (
        db_session.query(Quote).filter(Quote.category == "multiple_quote").all()
    )
    assert len(retrieved_quotes) == 3
    retrieved_authors = set(quote.author for quote in retrieved_quotes)
    assert retrieved_authors == {"Peter1", "Peter2", "Peter3"}


def test_empty_database(db_session) -> None:

    """
    Test the database is empty

    Returns: None

    """
    db_session.query(Quote).delete()
    db_session.commit()
    retrieved_quotes = db_session.query(Quote).all()
    assert len(retrieved_quotes) == 0
