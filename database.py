import sys

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Instance of declarative base
# Will let sqlalchemy know that classes are special sqlalchemy classes
Base = declarative_base()


class Category(Base):
    # Table name: category
    __tablename__ = 'category'

    # Mappers
    name = Column(String(30), nullable=False)                   # Category name
    description = Column(String(250), nullable=False)           # Category description
    url = Column(String(250), nullable=True)                    # Category image url
    id = Column(Integer, primary_key=True)                      # Category id

class Item(Base):
    # Table name: item
    __tablename__ = 'item'
    name = Column(String(30), nullable=False)                   # Item name
    description = Column(String(250), nullable=False)           # Item description
    url = Column(String(250), nullable=True)                    # Item picture URL, no picture needed
    id = Column(Integer, primary_key = True)
    category_id = Column(Integer, ForeignKey('category.id'))

    # Relationship with class Category
    category = relationship(Category)

# Create instance of create_engine class and point to database we will use
# Probably have to use sqlite for now
# engine = create_engine('postgresql+psycopg2:///catalogDatabase')
engine = create_engine('sqlite:///catalogDatabase')

Base.metadata.create_all(engine)


