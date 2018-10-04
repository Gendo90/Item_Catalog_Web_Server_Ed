import sys
from sqlalchemy import Column, ForeignKey, Integer, String
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

    title = Column(String(100))

    author = Column(String(100))

    description = Column(String(300))

    genre_id = Column(Integer, ForeignKey('genre.id'))

    genre = relationship(Genre)



#end of code!

engine = create_engine(
'sqlite:///booklist.db')

Base.metadata.create_all(engine)
