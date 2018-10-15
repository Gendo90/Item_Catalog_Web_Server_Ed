from flask import Flask, render_template, url_for
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, BookItem

engine = create_engine('sqlite:///booklist.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


import urllib


# Main page for the website
@app.route('/')
def mainPage():
    return render_template('index-logged-in.html')

# login page for the website
@app.route('/login/')
def loginPage():
    return render_template('login.html')

# code from project.py listing books by genre
@app.route("/genres/<int:genre_id>/")
def listGenre(genre_id):
    genre = session.query(Genre).filter_by(id = genre_id).one()
    genreBooks = session.query(BookItem).filter_by(genre_id = genre.id).all()

    return render_template('genre_list.html', genre=genre, bookList=genreBooks) # NEED TO SHOW BOOKS IN GENRE HERE?

# Book Viewer page for the website
@app.route('/fiction/<int:genre_id>/<int:book_id>/view')    #api key: AIzaSyC8gjeQNTOd8EUSKB-A8kCT8JDZaL0zIQM
def viewPage(genre_id, book_id):
    try:
        book = session.query(BookItem).filter_by(id = book_id).one()
        title = urllib.parse.quote(book.title)
        #image search api uri: "https://www.googleapis.com/customsearch/v1?q={{parse_title}}&cx=012831379883745738680%3Azo50lyeowzu&num=1&searchType=image&key=AIzaSyC8gjeQNTOd8EUSKB-A8kCT8JDZaL0zIQM"
        if len(book.author)==1:
            return render_template('book-viewer.html', book = book, parse_title = title, author=book.author[0])
        else:
            authors = ""
            for author in book.author:
                authors += author + ", "
            authors = authors[:len(authors)-2]
            return render_template('book-viewer.html', book = book, parse_title = title, author = authors)

    except:
        genres = session.query(Genre).all()
        outputI = "Genre IDs:"
        for i in genres:
            outputI += " " + str(i.id) + "    "
        books = session.query(BookItem).all()
        outputII = "Book IDs:"
        for n in books:
            outputII += " " + str(n.id) + "    "
        return outputI + outputII

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5500)
