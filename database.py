from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Instance of declarative base
# Will let sqlalchemy know that classes are special sqlalchemy classes
Base = declarative_base()


class User(Base):
    # Table name: user
    __tablename__ = 'user'
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    picture = Column(String(250))
    id = Column(Integer, primary_key=True)


class Category(Base):
    # Table name: category
    __tablename__ = 'category'

    # Mappers
    # Category name
    name = Column(String(30), nullable=False)
    # Category description
    description = Column(String(250), nullable=False)
    # Category image url
    url = Column(String(250), nullable=True)
    # Category id
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'img_url': self.url,
            'id': self.id,
        }


class Item(Base):
    # Table name: item
    __tablename__ = 'item'
    # Item name
    name = Column(String(30), nullable=False)
    # Item description
    description = Column(String(250), nullable=False)
    # Item picture URL, no picture needed
    url = Column(String(250), nullable=True)
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    # Relationship with class Category
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    # Relationship with class user
    user = relationship(User)

    # To be able to add json endpoint
    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'img_url': self.url,
            'id': self.id,
        }

# Create instance of create_engine class and point to database we will use
# engine = create_engine('postgresql+psycopg2:///catalogDatabase')
engine = create_engine('sqlite:///catalogDatabaseWithUsers')

Base.metadata.create_all(engine)


