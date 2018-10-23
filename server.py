from flask import Flask, render_template, url_for, request, redirect, jsonify, flash
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, SuperCategory, Genre, BookItem

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

# First of three super-categories that link to different pages - refactor
# later to make the three super-categories part of a table in the database
@app.route("/<string:super_category_name>/")
def superCategoryMainPage(super_category_name):
    thisCategory = session.query(SuperCategory).filter_by(name=super_category_name).one()
    containedGenres = session.query(Genre).filter_by(super_category_id=thisCategory.id).all()

    return render_template('genreIndex.html', superCategory=thisCategory.name, genres=containedGenres)

# code from project.py listing books by genre
@app.route("/<string:super_category_name>/<int:genre_id>/")
def listGenre(super_category_name, genre_id):
    genre = session.query(Genre).filter_by(id = genre_id).one()
    genreBooks = session.query(BookItem).filter_by(genre_id = genre.id).all()

    return render_template('genre-list.html', super_category_name=super_category_name, genre=genre, bookList=genreBooks) # NEED TO SHOW BOOKS IN GENRE HERE?

# Book Viewer page for the website
@app.route('/<string:super_category_name>/<int:genre_id>/<int:book_id>/view')    #api key: AIzaSyC8gjeQNTOd8EUSKB-A8kCT8JDZaL0zIQM
def viewPage(super_category_name, genre_id, book_id):
    genre = session.query(Genre).filter_by(id = genre_id).one()
    genreBooks = session.query(BookItem).filter_by(genre_id = genre.id).all()
    try:
        book = session.query(BookItem).filter_by(id = book_id).one()
        title = urllib.parse.quote(book.title)
        #image search api uri: "https://www.googleapis.com/customsearch/v1?q={{parse_title}}&cx=012831379883745738680%3Azo50lyeowzu&num=1&searchType=image&key=AIzaSyC8gjeQNTOd8EUSKB-A8kCT8JDZaL0zIQM"
        if len(book.author)==1:
            return render_template('book-viewer.html', super_category_name=super_category_name, genre=genre, genreBooks=genreBooks, book = book, parse_title = title, author=book.author[0])
        else:
            authors = ""
            for author in book.author:
                authors += author + ", "
            authors = authors[:len(authors)-2]
            return render_template('book-viewer.html', super_category_name=super_category_name, genre=genre, genreBooks=genreBooks, book = book, parse_title = title, author = authors)

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

# inaccessible webpage (uses POST method only) that deletes a book from a genre
@app.route('/<string:super_category_name>/<int:genre_id>/<int:book_id>/delete', methods=['POST'])
def deleteBook(super_category_name, genre_id, book_id):
    thisBook = session.query(BookItem).filter_by(id = book_id).one()
    title = thisBook.title
    session.delete(thisBook)
    session.commit()
    flash(title + " removed!")
    return render_template('index-logged-in.html')

# inaccessible webpage (uses POST method only) that edits a book's description
@app.route('/<string:super_category_name>/<int:genre_id>/<int:book_id>/edit', methods=['POST'])
def editBook(super_category_name, genre_id, book_id):
    thisBook = session.query(BookItem).filter_by(id = book_id).one()
    thisBook.description = request.form['updated_description']
    title = thisBook.title
    session.commit()
    flash(title + "'s description edited!")
    return redirect(url_for('viewPage', super_category_name=super_category_name, genre_id=genre_id, book_id=book_id))

# inaccessible webpage (uses POST method only) that creates a new book
@app.route('/newbook', methods=['GET', 'POST'])
def addBook():
    if(request.method=='POST'):
        title = request.form['title']
        author = request.form['author']
        desc = request.form['description']
        genre = request.form['genre']
        try:
            thisGenre=session.query(Genre).filter_by(name=genre).one()
            newBook = BookItem(title=title, author=[author],
            description=desc,
            genre=thisGenre, imgURL=None)
            session.add(newBook)
            session.commit()
            thisBook = session.query(BookItem).filter_by(title=newBook.title).one()
            flash(thisBook.title + " added!")
            return redirect(url_for('viewPage', super_category_name=thisGenre.super_category.name, genre_id=thisBook.genre_id,
            book_id=thisBook.id))
        except:
            allGenres = session.query(Genre).all()
            return render_template('new-book.html', allGenres=allGenres)
    else:
        allGenres = session.query(Genre).all()
        return render_template('new-book.html', allGenres=allGenres)

# inaccessible webpage (uses POST method only) that sets the imgURL property
# for a book
@app.route('/<string:super_category_name>/<int:genre_id>/<int:book_id>/cover_pic/<path:imgLocation>', methods=['POST'])
def setCoverImg(super_category_name, genre_id, book_id, imgLocation):
    thisBook = session.query(BookItem).filter_by(id = book_id).one()
    thisBook.imgURL = str(imgLocation)
    session.commit()
    return redirect(url_for('viewPage', super_category_name=super_category_name, genre_id=genre_id, book_id=book_id))

# used to get the JSON info for a particular book
@app.route('/<string:super_category_name>/<int:genre_id>/<int:book_id>/JSON')
def singleBookJSON(super_category_name, genre_id, book_id):
    try:
        book = session.query(BookItem).filter(
            BookItem.genre_id == genre_id, BookItem.id==book_id).one()
        genre = session.query(Genre).filter_by(id=genre_id).one()
        return jsonify(BookItems=[book.serialize])
    except:
        return "That genre id and/or book id could not be found!"

# used to get the JSON info for an entire genre
@app.route('/<string:super_category_name>/<int:genre_id>/JSON')
def genreBooksJSON(super_category_name, genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    items = session.query(BookItem).filter_by(
        genre_id=genre_id).all()
    return jsonify(BookItems=[i.serialize for i in items])

# used to get the JSON info for an entire supercategory
@app.route('/<string:super_category_name>/JSON/')
def superCategoryJSON(super_category_name):
    super_category = session.query(SuperCategory).filter_by(name=super_category_name).one()
    genresInCategory = session.query(Genre).filter_by(super_category_id=super_category.id).all()
    return jsonify(Genre=[i.serialize for i in genresInCategory])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=5500)
