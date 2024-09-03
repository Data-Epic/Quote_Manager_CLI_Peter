from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()   

class Quote(Base):
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String)
    author = Column(String)
    quote = Column(String)