from flask import Flask, render_template, url_for
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, BookItem

engine = create_engine('sqlite:///booklist.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


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

    return render_template('genre_list.html', genre=genre, bookList=genreBooks)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5500)
