from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Quote(Base):

    __tablename__ = "quotes"

    id: int = Column(Integer, primary_key=True, index=True)
    category: Optional[str] = Column(String(50), nullable=False)
    author: str = Column(String(100), nullable=False)
    quote: str = Column(String(500), nullable=False)
    created_at: DateTime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: DateTime = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"<Quote(id={self.id}, author='{self.author}', category='{self.category}')>"
        )
