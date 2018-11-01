import sys
from sqlalchemy import Column, ForeignKey, Integer, String, PickleType
# from sqlalchemy_imageattach.entity import Image, image_attachment
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    name = Column(
        String(40), nullable=False)

    picture = Column(
        String(250))

    email = Column(
        String(60), nullable=False)

    id = Column(
        Integer, primary_key=True)


class SuperCategory(Base):
    __tablename__ = 'super_category'

    name = Column(
        String(25), nullable=False)

    id = Column(
        Integer, primary_key=True)


class Genre(Base):
    __tablename__ = 'genre'

    name = Column(
        String(80), nullable=False)

    id = Column(
        Integer, primary_key=True)

    super_category_id = Column(
        Integer, ForeignKey('super_category.id'), nullable=False)

    super_category = relationship(SuperCategory)

    user_id = Column(
        Integer, ForeignKey('user.id'), nullable=False)

    user = relationship(User)

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

    id = Column(Integer, primary_key=True)

    title = Column(String(100), nullable=False)

    author = Column(PickleType(), nullable=False)

    description = Column(String(600))

    imgURL = Column(String(100))

    genre_id = Column(Integer, ForeignKey('genre.id'), nullable=False)

    genre = relationship(Genre)

    user_id = Column(
        Integer, ForeignKey('user.id'), nullable=False)

    user = relationship(User)

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


engine = create_engine(
        'sqlite:///booklistwithusers.db')

Base.metadata.create_all(engine)
