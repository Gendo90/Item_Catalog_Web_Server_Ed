import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

#write code here!





#end of code!

engine = create_engine(
'sqlite:///booklist.db')

Base.metadata.create_all(engine)
