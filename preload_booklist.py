from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, BookItem

engine = create_engine('sqlite:///booklist.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#Add basic genres
Genre_I = Genre(name="Fantasy")
session.add(Genre_I)

Genre_II = Genre(name="Science Fiction")
session.add(Genre_II)

Genre_III = Genre(name="Self-Help")
session.add(Genre_III)

Genre_IV = Genre(name="Law")
session.add(Genre_IV)


#Add one book per genre to start!
Book_I = BookItem(title="The Hobbit", author="J.R.R. Tolkien",
description="A classic fantasy adventure masterpiece, which introduces \
Middle-Earth to most readers, and serves as a prequel to Tolkien's Lord of the \
Rings epic saga.", genre=Genre_I)
session.add(Book_I)

Book_II = BookItem(title="Hyperion", author="Dan Simmons",
description="A Hugo Award-winning science fiction novel, which details the \
journey of a special force of 'pilgrims' to the planet Hyperion, who were \
all connected to the planet in the past and are now tasked with unravelling \
its secrets. Story is comprised of multiple narrative accounts of the 'pilgrims'\
past connection to Hyperion, and is structured in the same way as the \
Canterbury Tales - stories told on-route to their destination!",
genre=Genre_II)
session.add(Book_II)

Book_III = BookItem(title="Willpower: Rediscovering the Greatest Human Strength",
 author=["Roy F. Baumeister", "John Tierney"], description="A book written by \
 a psychologist and a journalist examining the modern history and study of \
 the trait of 'willpower', and giving advice on how to use and improve it in \
 your daily life!",
genre=Genre_III)
session.add(Book_III)

Book_IV = BookItem(title="Law for Dummies",
 author=["John Ventura"], description="""A book written by
 a lawyer that explains the basics of different areas of the law, especially
 common occurences and legal tips that are directly applicable to the reader's
 life, like contracts and family law.""",
genre=Genre_IV)
session.add(Book_IV)


#Commit all changes made to booklist.db!
session.commit()
