import sys
from sqlalchemy import Column, ForeignKey, Integer, String, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

#write code here!

class Genre(Base):
    __tablename__ = 'genre'

    name = Column(
    String(80), nullable = False)

    id = Column(
    Integer, primary_key = True)


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
