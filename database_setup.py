import sys
from sqlalchemy import Column, ForeignKey, Integer, String, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

#write code here!

class SuperCategory(Base):
    __tablename__ = 'super_category'

    name = Column(
    String(25), nullable = False)

    id = Column(
    Integer, primary_key = True)

class Genre(Base):
    __tablename__ = 'genre'

    name = Column(
    String(80), nullable = False)

    id = Column(
    Integer, primary_key = True)

    super_category_id = Column(
    Integer, ForeignKey('super_category.id'), nullable = False)

    super_category = relationship(SuperCategory)

    # We added this serialize function to be able to send JSON objects in a
    # serializable format
    @property
    def serialize(self):

        return {
            'name': self.name,
            'id': self.id,
            'super_category': self.super_category.name
        }


class BookItem(Base):
    __tablename__ = 'book_item'

    id = Column(Integer, primary_key = True)

    title = Column(String(100), nullable = False)

    author = Column(PickleType(), nullable=False)#String(100), nullable = False)

    description = Column(String(600))

    imgURL = Column(String(100))

    genre_id = Column(Integer, ForeignKey('genre.id'), nullable = False)

    genre = relationship(Genre)

    # We added this serialize function to be able to send JSON objects in a
    # serializable format
    @property
    def serialize(self):

        return {
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'image_URL': self.imgURL,
            'id': self.id,
            'genre': self.genre.name
        }



#end of code!

engine = create_engine(
'sqlite:///booklist.db')

Base.metadata.create_all(engine)
