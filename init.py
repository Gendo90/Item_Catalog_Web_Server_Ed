#!/usr/lib/python3 python3
from flask import Flask, render_template, url_for, redirect, jsonify, flash
from flask import request

from sqlalchemy import create_engine, exists, func, distinct
from sqlalchemy.orm import sessionmaker, exc, aliased
from database_setup import Base, User, SuperCategory, Genre, BookItem

# import packages for anti-forgery state token creation
from flask import session as login_session
import random
import string

# import packages to prevent caching on cloudfront
from flask import make_response
from datetime import datetime
import functools

# import packages for google oauth login
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import urllib

# import database packages
# import postgresql
import psycopg2

# get packages for cover pic images
import boto3
import urllib.request
import os

# create the flask object "app"
app = Flask(__name__)

# Some global variables that are used in the GConnect function
# NOTE: need to download the 'client_secrets.json' from the google account
# AFTER updating the certification on the google account to allow redirection
# to BOTH http://localhost:8000/login and http://localhost:8000/gconnect
# or it will not work
with app.open_resource('client_secrets.json') as f:
	byte_output = f.read()
	CLIENT_ID = json.loads(str(byte_output.decode('utf-8')))['web']['client_id']
APPLICATION_NAME = "Book Collector App"

engine = create_engine(
        'postgresql+psycopg2://admin:Aoq7M9@localhost/books')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

CustomSearchAPIKEY = "AIzaSyC8gjeQNTOd8EUSKB-A8kCT8JDZaL0zIQM"

app.secret_key = 'SECOND_secret_key_here!'

# app.config['SERVER_NAME'] = 'bestbookcollection.com'


# Main page for the website
@app.route('/')
def mainPage():
    # this code adds the three main supercategories upon starting the server
    # if they are not already present in the database file
    try:
        print("TEST")
        session.query(SuperCategory).filter_by(name='Fiction').one()
    except exc.NoResultFound:
        # add super-categories that contain the genres
        SuperCategory_I = SuperCategory(name="Fiction")
        session.add(SuperCategory_I)

        SuperCategory_II = SuperCategory(name="Non-Fiction")
        session.add(SuperCategory_II)

        SuperCategory_III = SuperCategory(name="Reference")
        session.add(SuperCategory_III)

        session.commit()
        print("Made SuperCategories!")

    try:
        login_session['user_id']
    except KeyError:
        login_session['user_id'] = -0.1

    return render_template('index-logged-in.html')

# function to prevent caching on the routing server
def nocache(view):
    @functools.wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return functools.update_wrapper(no_cache, view)

TESTVAR = 0

# login page for the website
# Create a state token to prevent request forgery.
# Store it in the session for later validation
# Show login verification page
@app.route('/login/')
def loginPage():
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in range(32))
    login_session['state'] = 0
    login_session['state'] = state
    TESTVAR = state
    print("The set login state key is "+login_session['state'])
    return render_template('login.html', STATE=state)


# User Helper Functions - work with the User class of objects from the
# database_setup.py file to create and get information about logged-in
# website users

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except exc.NoResultFound:
        return None


# GConnect code to authenticate user using the google API
# With the "client secret" and client # ID
# ALso verifies that the request comes from the browser with the same
# anti-forgery state token as the one provided by the browser.
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    print("The login state is: " +login_session['state'])
    print("THE TESTVAR IS " + str(TESTVAR))
    print("The given state is: " + request.args['state'])
    try:
        if request.args['state'] != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
    except KeyError:
        response = make_response(json.dumps('No state parameter included'), 401)
        response.headers['Content-Type'] = 'application/json'
        print("State parameter error")
        return response

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/html/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
                json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    g_byte_resp = h.request(url, 'GET')[1]
    result = json.loads(str(g_byte_resp.decode('utf-8')))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
            -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")

    # checks if this User already exists in the database - if not, adds them!
    if(getUserID(login_session['email']) is None):
        createUser(login_session)

    login_session['user_id'] = getUserID(login_session['email'])
    print('Your username is: ' +login_session['username'])
    print('Your UserID is: ' + str(login_session['user_id']))
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
# for Google logins/users only!
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
                                'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is {}'.format(access_token))
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(
                login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    resp, result2 = h.request(url, 'GET')
    print("The second result is: ")
    print(result2)
    if result['status'] == '200':
        # user_id field is always an integer as defined in the User class, so
        # if there is no user currently logged-in to the site, setting the
        # user_id to a fraction here signifies that no valid user is
        # currently logged-in
        login_session['user_id'] = -0.1
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    elif (json.loads(result2)["error_description"] ==
            "Token expired or revoked"):
        # user_id field is always an integer as defined in the User class, so
        # if there is no user currently logged-in to the site, setting the
        # user_id to a fraction here signifies that no valid user is
        # currently logged-in
        login_session['user_id'] = -0.1
        response = make_response(json.dumps('Token already revoked \
                    - disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token \
                    for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print("access token received {} ".format(access_token))
    # loads fb client secret from downloaded .json file here
    with app.open_resource('fb_client_secrets.json') as f:
        fb_byte_resp = f.read()
        app_id = json.loads(str(fb_byte_resp.decode('utf-8')))[
            'web']['app_id']
        app_secret = json.loads(
            str(fb_byte_resp.decode('utf-8')))['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?\
            grant_type=fb_exchange_token&client_id={}&client_secret={}&\
            fb_exchange_token={}'.format(
        app_id, app_secret, access_token.decode('utf-8'))  # access token must
    # be decoded here because it is in bytes not string
    print(url.replace(" ", ""))
    h = httplib2.Http()
    result = h.request(url.replace(" ", ""), 'GET')[1]
    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v3.2/me"
    '''
        Due to the formatting for the result from the server token exchange we
        have to split the token first on commas and select the first index
        which gives us the key : value for the server access token then we
        split it on colons to pull out the actual token value and replace the
        remaining quotes with nothing so that it can be used directly in the
        graph api calls
    '''
    print(result)
    # result must be decoded because it is in bytes not string
    token = result.decode("utf-8").split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v3.2/\
    me?access_token=%s&fields=name,id,email' % token
    print(url.replace(" ", ""))
    h = httplib2.Http()
    result = h.request(url.replace(" ", ""), 'GET')[1]
    fb_auth_resp = result.decode('utf-8')
    data = json.loads(str(fb_auth_resp))
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v3.2/me/picture?\
            access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url.replace(" ", ""), 'GET')[1]
    data = json.loads(result.decode('utf-8'))

    login_session['picture'] = data["data"]["url"]

    # see if user exists by checking id from online user vs. this site's
    # database
    user_id = getUserID(login_session['email'])
    print(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
                -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must be included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/{}/permissions?\
            access_token={}'.format(facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url.replace(" ", ""), 'DELETE')[1]
    return "you have been logged out"


# Disconnect based on provider - will disconnect for both Google and Facebook
# OAuth sessions presently
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        # remove empty genres for this user that have no books in them!
        # must be done before login_session['email'] is deleted
        user_id = getUserID(login_session['email'])
        user_Genres = session.query(Genre).filter_by(user_id=user_id).all()
        for genre in user_Genres:
            user_Books = session.query(BookItem).filter(
                BookItem.user_id == user_id,
                BookItem.genre_id == genre.id).all()
            if user_Books == []:
                print("Removing '" + genre.name + "' user's genres!")
                session.delete(genre)
                session.commit()
                flash("'" + genre.name + "' genre removed - empty of books!")
        del login_session['email']
        del login_session['picture']
        login_session['user_id'] = -0.1
        del login_session['provider']
        flash("You have successfully been logged out.")
        return render_template('index-logged-in.html')
    else:
        flash("You were not logged in")
        return render_template('index-logged-in.html')


# Three super-categories that link to different pages - the string name should
# be "Fiction", "Non-Fiction", or "Reference" to get valid results for the
# genres in those super-categories
@app.route("/<string:super_category_name>/")
def superCategoryMainPage(super_category_name):
    thisCategory = session.query(
            SuperCategory).filter_by(name=super_category_name).one()
    print("The supercategory name  is " + thisCategory.name)
    try:
        # modified so that it only shows one genre if there are multiple with
        # the same name (e.g. two different "Fantasy" genres for different
        # user id's will only show once)
        containedGenres = session.query(
                Genre.super_category_id, Genre.name).filter_by(
                super_category_id=thisCategory.id).group_by( # removed a "from_self" here, added an order_by
                    Genre.super_category_id, Genre.name).all()

        return render_template(
            'genreIndex.html',
            superCategory=thisCategory.name, genres=containedGenres)
    except exc.NoResultFound or exc.ProgrammingError:
        # case where there are no genres or books for this user yet - like
        # a new user!
        return render_template(
            'genreIndex.html',
            superCategory=thisCategory.name, genres=[])


# webpage listing books within a particular genre - for ALL users with that
# genre!
@app.route("/<string:super_category_name>/<string:genre_name>/")
def listGenre(super_category_name, genre_name):
    genreBooks = session.query(BookItem.title).join(
        Genre, Genre.id == BookItem.genre_id).filter(
        Genre.name == genre_name).group_by(BookItem.title)

    return render_template(
        'genre-list.html',
        super_category_name=super_category_name, genre=genre_name,
        bookList=genreBooks)  # NEED TO SHOW BOOKS IN GENRE HERE?


# Book Viewer page for the website
@app.route('/<string:super_category_name>/\
        <string:genre_name>/<string:book_title>/view'.replace(" ", ""))
def viewPage(super_category_name, genre_name, book_title):
    # ensures there is a login session user id to compare against
    try:
        login_session['user_id']
    except KeyError:
        login_session['user_id'] = -0.1
    # new plan - get duplicate book titles first, then check book titles vs
    # duplicate book titles, then remove duplicate book titles
    # update this genre query so that it returns all books for the given
    # genre, regardless of the user
    genreBooks = session.query(BookItem.title).join(
        Genre, Genre.id == BookItem.genre_id).filter(
        Genre.name == genre_name).group_by(BookItem.title)
    # find duplicate book entries to set up the link to the duplicate page!
    book = session.query(BookItem).filter_by(title=book_title).first()
    duplicateBooks = session.query(BookItem.title).join(
        Genre, Genre.id == BookItem.genre_id).filter(
        Genre.name == genre_name, BookItem.title == book.title).count()
    if(duplicateBooks > 1):
        isDuplicate = True
        try:
                book = session.query(BookItem).filter(BookItem.title == book_title,
                BookItem.user_id == login_session['user_id']).one()
        except:
                book = session.query(BookItem).filter_by(title=book_title).first()
        print(url_for('duplicateBookViewer', super_category_name=super_category_name,
            genre_name=genre_name, book_id=book.id, _external=True))
        return redirect(url_for(
            'duplicateBookViewer', super_category_name=super_category_name,
            genre_name=genre_name, book_id=book.id, _external=True).replace("http://", "https://www."))
    # code that determines if there are one or more authors for the book
    if len(book.author) == 1:
        # makes sure the page only loads the edit and delete info if the
        # user is logged in and it is their book!
        if(login_session['user_id'] == book.user_id):
            return render_template(
                'book-viewer.html',
                API_KEY=CustomSearchAPIKEY,
                super_category_name=super_category_name, genre=genre_name,
                genreBooks=genreBooks, book=book,
                author=book.author[0])
        else:
            return render_template(
                'book-viewer-logged-out.html',
                super_category_name=super_category_name, genre=genre_name,
                genreBooks=genreBooks, book=book,
                author=book.author[0])
    else:
        authors = ""
        for author in book.author:
            authors += author + ", "
        authors = authors[:len(authors)-2]
        # makes sure the page only loads the edit and delete info if the
        # user is logged in and it is their book!
        if(login_session['user_id'] == book.user_id):
            return render_template(
                'book-viewer.html',
                API_KEY=CustomSearchAPIKEY,
                super_category_name=super_category_name,
                genre=genre_name, genreBooks=genreBooks, book=book,
                author=authors)
        else:
            return render_template(
                'book-viewer-logged-out.html',
                super_category_name=super_category_name,
                genre=genre_name, genreBooks=genreBooks, book=book,
                author=authors)


# Viewer for duplicate books on the website
@app.route('/<string:super_category_name>/\
        <string:genre_name>/<int:book_id>/view/duplicates'.replace(" ", ""))
def duplicateBookViewer(super_category_name, genre_name, book_id):
    book = session.query(BookItem).filter_by(id=book_id).one()
    bookCopies = session.query(BookItem).filter_by(title=book.title).all()
    if len(book.author) == 1:
        if(login_session['user_id'] == book.user_id):
            return render_template(
                'duplicate-books.html',
                super_category_name=super_category_name,
                book=book, bookCopies=bookCopies, genre=genre_name,
                API_KEY=CustomSearchAPIKEY, author=book.author[0])
        else:
            return render_template(
                'duplicate-books-viewer-only.html',
                super_category_name=super_category_name, book=book,
                bookCopies=bookCopies, genre=genre_name, author=book.author[0])
    else:
        authors = ""
        for author in book.author:
            authors += author + ", "
        authors = authors[:len(authors)-2]
        # makes sure the page only loads the edit and delete info if the
        # user is logged in and it is their book!
        if(login_session['user_id'] == book.user_id):
            return render_template(
                'duplicate-books.html',
                super_category_name=super_category_name,
                book=book, bookCopies=bookCopies, genre=genre_name,
                API_KEY=CustomSearchAPIKEY, author=authors)
        else:
            return render_template(
                'duplicate-books-viewer-only.html',
                super_category_name=super_category_name, book=book,
                bookCopies=bookCopies, genre=genre_name, author=authors)


# inaccessible webpage (uses POST method only) that deletes a book from a genre
@app.route(
    '/<string:super_category_name>/<string:genre_name>/<int:book_id>/delete',
    methods=['POST'])
def deleteBook(super_category_name, genre_name, book_id):
    thisBook = session.query(BookItem).filter_by(id=book_id).one()
    # verifies that the book belongs to the user who sent the POST request
    # to set the image
    if(login_session['user_id'] == thisBook.user_id):
        title = thisBook.title
        session.delete(thisBook)
        session.commit()
        flash(title + " removed!")
        print(title + " removed!")
        return redirect(url_for('listGenre', super_category_name = super_category_name, genre_name=genre_name, _external=True).replace("http://", "https://www."))


# inaccessible webpage (uses POST method only) that edits a book's description
@app.route(
    '/<string:super_category_name>/<string:genre_name>/<int:book_id>/edit',
    methods=['POST'])
def editBook(super_category_name, genre_name, book_id):
    thisBook = session.query(BookItem).filter_by(id=book_id).one()
    # verifies that the book belongs to the user who sent the POST request
    # to change the description
    if(login_session['user_id'] == thisBook.user_id):
        thisBook.description = request.form['updated_description']
        title = thisBook.title
        session.commit()
        flash(title + "'s description edited!")
        print("Edit redirect to " + url_for('viewPage', API_KEY=CustomSearchAPIKEY,
            super_category_name=super_category_name, genre_name=genre_name, book_title=thisBook.title,
            _external=True).replace("http://", "https://www."))
        return redirect(url_for(
            'viewPage', API_KEY=CustomSearchAPIKEY,
            super_category_name=super_category_name,
            genre_name=genre_name, book_title=thisBook.title, _external=True).replace("http://", "https://www."))


# webpage that creates a new book
@app.route('/newbook', methods=['GET', 'POST'])
def addBook():
    try:
        user_id = login_session["user_id"]
        if(request.method == 'POST'):
            title = request.form['title']
            author = request.form['author']
            desc = request.form['description']
            genre = request.form['genre']
            thisGenre = session.query(Genre).filter(
                Genre.name == genre, Genre.user_id == user_id).one()
            # checks to see if book title and genre are duplicates, will
            # not add them if they both are
            if(not session.query(exists().where(
                    BookItem.title == title).where(
                    BookItem.user_id == thisGenre.user_id)).scalar()):
                    newBook = BookItem(
                        title=title, author=[author], description=desc,
                        genre=thisGenre, imgURL=None,
                        user_id=thisGenre.user_id)
                    session.add(newBook)
                    session.commit()
                    thisBook = session.query(BookItem).filter(
                            BookItem.title == title,
                            BookItem.user_id == user_id).one()
                    print(thisBook.title)
                    flash(thisBook.title + " added!")
            else:
                thisBook = session.query(BookItem).filter(
                    BookItem.title == title,
                    BookItem.genre_id == thisGenre.id).one()
                flash(thisBook.title + " already exists in your collection!")

            return redirect(url_for(
                'viewPage',
                super_category_name=thisGenre.super_category.name,
                genre_name=genre, book_title=thisBook.title, _external=True).replace("http://", "https://www."))
        else:
            allMyGenres = session.query(Genre).filter_by(user_id=user_id).all()
            return render_template('new-book.html', allGenres=allMyGenres)
    except KeyError:
        return redirect(url_for('loginPage', _external=True).replace("http://", "https://www."))


# webpage that sets the imgURL property for a book so that a picture appears
# on the book-viewer page
@app.route(
        '/<string:super_category_name>/<string:genre_name>/\
        <int:book_id>/cover_pic/<path:imgLocation>'.replace(" ", ""),
        methods=['POST'])
def setCoverImg(super_category_name, genre_name, book_id, imgLocation):
    thisBook = session.query(BookItem).filter_by(id=book_id).one()
    # verifies that the book belongs to the user who sent the POST request
    # to set the image
    if(login_session['user_id'] == thisBook.user_id and
            thisBook.imgURL is None):
        imgPathURL = str(imgLocation)
        filename = str(imgLocation).replace("/", "_").replace(":", "_").replace("http", "_")
        print(filename)
        if(imgPathURL.startswith("https")):
            imgPathURL=imgPathURL.replace("https:/", "https://")
        elif(imgPathURL.startswith("http")):
            imgPathURL=imgPathURL.replace("http:/", "http://")
        print(imgPathURL)
        os.chdir('/var/www/html/static/covers')
        f = open(filename, 'wb')
        f.write(urllib.request.urlopen(imgPathURL).read())
        thisBook.imgURL = filename
        session.commit()
        f.close()
        os.chdir('/var/www/html')
        print(thisBook.imgURL)
        return redirect(url_for(
            'viewPage', API_KEY=CustomSearchAPIKEY,
            super_category_name=super_category_name,
            genre_name=genre_name, book_title=thisBook.title, _external=True).replace('http://', "https://www."))


# webpage that creates a new genre, with a form that uses POST to send the
# server a genre name and super-category the user enters
# Accessible from the new-book page, so that the user can conveniently add a
# genre before adding a book to it!
@app.route('/newgenre', methods=['GET', 'POST'])
def addGenre():
    if(request.method == 'POST'):
        name = request.form['name']
        superCategoryName = request.form['category']
        user_id = login_session['user_id']
        # checks to see if the genre is a duplicate, will
        # not add it if it is a duplicate e.g. already exists)
        if(not session.query(exists().where(
                Genre.name == name).where(
                Genre.user_id == user_id)).scalar()):
            superCategory = session.query(
                    SuperCategory).filter_by(name=superCategoryName).one()
            newGenre = Genre(
                    name=name,
                    super_category=superCategory, user_id=user_id)
            session.add(newGenre)
            session.commit()
            flash(newGenre.name + " genre added!")
            allMyGenres = session.query(Genre).filter_by(user_id=user_id).all()
            return render_template('new-book.html', allGenres=allMyGenres)
        else:  # case where the genre is a duplicate
            flash(name + " is already a genre!")
            superCategories = session.query(SuperCategory).all()
            return render_template(
                        'new-genre.html',
                        allSuperCategories=superCategories)
    else:  # returns page for "new-genre.html" upon a GET request
        superCategories = session.query(SuperCategory).all()
        return render_template(
                    'new-genre.html',
                    allSuperCategories=superCategories)


# used to get the JSON info for a particular book
@app.route('/<string:super_category_name>/\
            <string:genre_name>/<int:book_id>/JSON'.replace(" ", ""))
def singleBookJSON(super_category_name, genre_name, book_id):
    try:
        # searches within all genres with the given genre_name to find a
        # book with the given book_id (i.e. verifies that the genre indeed
        # contains this book in order for the JSON to be returned)
        book = session.query(BookItem).join(
            Genre, Genre.id == BookItem.genre_id).filter(
            Genre.name == genre_name).filter(
                    BookItem.id == book_id).one()
        return jsonify(BookItems=[book.serialize])
    except exc.NoResultFound:
        return "That genre name and book id combination could not be found!"

# used to get the JSON info for a particular book
@app.route('/<string:super_category_name>/\
            <string:genre_name>/<int:book_id>/JSON/'.replace(" ", ""))
def rerouteToSingleBookJSON(super_category_name, genre_name, book_id):
    # routes back to the 'singleBookJSON' function
    return redirect(url_for('singleBookJSON', super_category_name=super_category_name,
    genre_name=genre_name, book_id=book_id, _external=True).replace('http://', 'https://www.'))


# used to get the JSON info for an entire genre
@app.route('/<string:super_category_name>/<string:genre_name>/JSON')
def genreBooksJSON(super_category_name, genre_name):
    # items gives all the books in the genre(s) that match the given
    # genre_name - there may be different users with books in the same genre,
    # but they are technically separate "genres" in the database
    items = session.query(BookItem).join(
        Genre, Genre.id == BookItem.genre_id).filter(
        Genre.name == genre_name).all()
    return jsonify(BookItems=[i.serialize for i in items])

# allows this route to get the JSON info for an entire genre as well
@app.route('/<string:super_category_name>/<string:genre_name>/JSON/')
def rerouteToGenreBooksJSON(super_category_name, genre_name):
    # routes back to the 'genreBooksJSON' function
    return redirect(url_for('genreBooksJSON', super_category_name=super_category_name,
    genre_name=genre_name, _external=True).replace('http://', 'https://www.'))


# used to get the JSON info for an entire supercategory
@app.route('/<string:super_category_name>/JSON')
def superCategoryJSON(super_category_name):
    # single SQL query to get all genre names within a given supercategory,
    # for all users' genres
    allMatchingGenres = session.query(Genre).join(
        SuperCategory, SuperCategory.id == Genre.super_category_id).filter(
        SuperCategory.name == super_category_name).group_by(Genre.name, Genre.id).all()
	# need to add more code here to make the JSON object query server-friendly
	# and still give the correct answer - need a GROUP_BY function using
	# Genre.id above or the server crashes.
    noDuplicateNames = []
    genresInCategory = []
    for i in allMatchingGenres:
        if i.name not in noDuplicateNames:
            noDuplicateNames.append(i.name)
            genresInCategory.append(i)
    response_json = jsonify(Genre=[i.serialize for i in genresInCategory])
    return response_json

# enables this route for the JSON information as well!
@app.route('/<string:super_category_name>/JSON/')
def rerouteToSuperCategoryJSON(super_category_name):
    # routes back to the 'superCategoryJSON' function
    return redirect(url_for('superCategoryJSON', super_category_name=super_category_name, _external=True).replace('http://', 'https://www.'))

if __name__ == '__main__':
    # secret key used here to enable flash messages
    app.secret_key = "SECOND_secret_key_here!"
    app.debug = True
    app.run(host='0.0.0.0', port=80)
