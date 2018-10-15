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


class BookItem(Base):
    __tablename__ = 'book_item'

    id = Column(Integer, primary_key = True)

    title = Column(String(100), nullable = False)

    author = Column(PickleType(), nullable=False)#String(100), nullable = False)

    description = Column(String(600))

    genre_id = Column(Integer, ForeignKey('genre.id'), nullable = False)

    genre = relationship(Genre)



#end of code!

engine = create_engine(
'sqlite:///booklist.db')

Base.metadata.create_all(engine)
