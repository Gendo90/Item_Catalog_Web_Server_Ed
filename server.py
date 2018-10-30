from flask import Flask, render_template, url_for, request, redirect, jsonify, flash
app = Flask(__name__)

from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, SuperCategory, Genre, BookItem

# import packages for anti-forgery state token creation
from flask import session as login_session
import random, string

# import packages for google oauth login
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# Some global variables that are used in the GConnect function
# NOTE: need to download the 'client_secrets.json' from the google account AFTER
# updating the certification on the google account to allow redirection to BOTH
# http://localhost:5000/login and http://localhost:5000/gconnect or it will not work
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Book Collector App"

engine = create_engine('sqlite:///booklistwithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

import urllib


CustomSearchAPIKEY="AIzaSyC8gjeQNTOd8EUSKB-A8kCT8JDZaL0zIQM"

# Main page for the website
@app.route('/')
def mainPage():
    # this code adds the three main supercategories upon starting the server
    # if they are not already present in the database file
    try:
        session.query(SuperCategory).filter_by(name='Fiction').one()
    except:
        # add super-categories that contain the genres
        SuperCategory_I = SuperCategory(name="Fiction")
        session.add(SuperCategory_I)

        SuperCategory_II = SuperCategory(name="Non-Fiction")
        session.add(SuperCategory_II)

        SuperCategory_III = SuperCategory(name="Reference")
        session.add(SuperCategory_III)

        session.commit()

    try:
        login_session['user_id']
    except:
        login_session['user_id'] = -0.1

    return render_template('index-logged-in.html')

# login page for the website
# Create a state token to prevent request forgery.
# Store it in the session for later validation
# Show login verification page
@app.route('/login/')
def loginPage():
    state = ''.join(random.choice(string.ascii_uppercase +
    string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# User Helper Functions


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
    except:
        return None


# GConnect code to authenticate user using the google API
# With the "client secret" and client # ID
# ALso verifies that the request comes from the browser with the same anti-forgery state
# token as the one provided by the browser.
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
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
    result = json.loads(h.request(url, 'GET')[1])
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
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")

    #checks if this User already exists in the database - if not, adds them!
    if(getUserID(login_session['email']) == None):
        createUser(login_session)

    login_session['user_id'] = getUserID(login_session['email'])
    return output

 # DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is {}'.format(access_token))
    print('User name is: ')
    print(login_session['username'])
    #add code here to purge All empty genres on logging out of the website
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    resp, result2 = h.request(url, 'GET')
    print("The second result is: ")
    print(result2)
    if result['status'] == '200':
        #del login_session['access_token'] # removed in the general disconnect function (LATER)
        #del login_session['gplus_id'] #'...'
        #del login_session['username']
        #del login_session['email']
        #del login_session['picture']
        login_session['user_id'] = -0.1;
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    elif (json.loads(result2)["error_description"] == "Token expired or revoked"):
        #del login_session['access_token'] # removed in the general disconnect function (LATER)
        #del login_session['gplus_id'] #'...'
        #del login_session['username']
        #del login_session['email']
        #del login_session['picture']
        login_session['user_id'] = -0.1
        response = make_response(json.dumps('Token already revoked - disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
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


    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token.decode('utf-8')) # access token must be decoded because it is in bytes not string
    print(url)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]


    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v3.2/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    print(result)
    token = result.decode("utf-8").split(',')[0].split(':')[1].replace('"', '') # result must be decoded because it is in bytes not string

    url = 'https://graph.facebook.com/v3.2/me?access_token=%s&fields=name,id,email' % token #was v2.8 before
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v3.2/me/picture?access_token=%s&redirect=0&height=200&width=200' % token #was v2.8 before
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email']) # does not work in my case because I use different emails?
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


 # Disconnect based on provider
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
        # must be done before user_id is deleted
        user_id = getUserID(login_session['email'])
        user_Genres = session.query(Genre).filter_by(user_id=user_id).all()
        for genre in user_Genres:
            user_Books = session.query(BookItem).filter(BookItem.user_id==user_id, BookItem.genre_id==genre.id).all()
            if user_Books==[]:
                print("Removing '" + genre.name + "' user's genres!")
                session.delete(genre)
                session.commit()
                flash("'" + genre.name + "' genre removed - empty of books!")
        del login_session['email']
        del login_session['picture']
        login_session['user_id'] = -0.1
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('mainPage'))
    else:
        flash("You were not logged in")
        return redirect(url_for('mainPage'))

# First of three super-categories that link to different pages - refactor
# later to make the three super-categories part of a table in the database
@app.route("/<string:super_category_name>/")
def superCategoryMainPage(super_category_name):
    thisCategory = session.query(SuperCategory).filter_by(name=super_category_name).one()
    try:
        containedGenres = session.query(Genre).filter_by(super_category_id=thisCategory.id).all()

        return render_template('genreIndex.html', superCategory=thisCategory.name, genres=containedGenres)
    except: # case where there are no genres or books for this user yet
        return render_template('genreIndex.html', superCategory=thisCategory.name, genres=[])

# code from project.py listing books by genre
@app.route("/<string:super_category_name>/<int:genre_id>/")
def listGenre(super_category_name, genre_id):
    genre = session.query(Genre).filter_by(id = genre_id).one()
    genreBooks = session.query(BookItem).filter_by(genre_id = genre.id).all()

    return render_template('genre-list.html', super_category_name=super_category_name, genre=genre, bookList=genreBooks) # NEED TO SHOW BOOKS IN GENRE HERE?

# Book Viewer page for the website
@app.route('/<string:super_category_name>/<int:genre_id>/<int:book_id>/view')    #api key: AIzaSyC8gjeQNTOd8EUSKB-A8kCT8JDZaL0zIQM
def viewPage(super_category_name, genre_id, book_id):
    #ensures there is a login session user id to compare against
    try:
        login_session['user_id']
    except:
        login_session['user_id'] = -0.1
    genre = session.query(Genre).filter_by(id = genre_id).one()
    genreBooks = session.query(BookItem).filter_by(genre_id = genre.id).all()
    try:
        book = session.query(BookItem).filter_by(id = book_id).one()
        title = urllib.parse.quote(book.title)
        if len(book.author)==1:
            # makes sure the page only loads the edit and delete info if the
            # user is logged in and it is their book!
            if(login_session['user_id']==book.user_id):
                return render_template('book-viewer.html',
                API_KEY=CustomSearchAPIKEY,
                super_category_name=super_category_name, genre=genre,
                genreBooks=genreBooks, book = book, parse_title = title,
                author=book.author[0])
            else:
                return render_template('book-viewer-logged-out.html',
                super_category_name=super_category_name, genre=genre,
                genreBooks=genreBooks, book = book, parse_title = title,
                author=book.author[0])
        else:
            authors = ""
            for author in book.author:
                authors += author + ", "
            authors = authors[:len(authors)-2]
            # makes sure the page only loads the edit and delete info if the
            # user is logged in and it is their book!
            if(login_session['user_id']==book.user_id):
                return render_template('book-viewer.html',
                API_KEY=CustomSearchAPIKEY, super_category_name=super_category_name,
                genre=genre, genreBooks=genreBooks, book = book,
                parse_title = title, author = authors)
            else:
                return render_template('book-viewer-logged-out.html',
                super_category_name=super_category_name,
                genre=genre, genreBooks=genreBooks, book = book,
                parse_title = title, author = authors)

    except: # debug code to see what is in the db
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
    if(login_session['user_id']==thisBook.user_id): #verifies that the book belongs to the user who sent the POST request to set the image
        title = thisBook.title
        session.delete(thisBook)
        session.commit()
        flash(title + " removed!")
        return render_template('index-logged-in.html')

# inaccessible webpage (uses POST method only) that edits a book's description
@app.route('/<string:super_category_name>/<int:genre_id>/<int:book_id>/edit', methods=['POST'])
def editBook(super_category_name, genre_id, book_id):
    thisBook = session.query(BookItem).filter_by(id = book_id).one()
    if(login_session['user_id']==thisBook.user_id): #verifies that the book belongs to the user who sent the POST request to change the description
        thisBook.description = request.form['updated_description']
        title = thisBook.title
        session.commit()
        flash(title + "'s description edited!")
        return redirect(url_for('viewPage', API_KEY = CustomSearchAPIKEY, super_category_name=super_category_name, genre_id=genre_id, book_id=book_id))

# webpage that creates a new book
@app.route('/newbook', methods=['GET', 'POST'])
def addBook():
    if(request.method=='POST'):
        title = request.form['title']
        author = request.form['author']
        desc = request.form['description']
        genre = request.form['genre']
        try:
            thisGenre=session.query(Genre).filter_by(name=genre).one()
            # checks to see if book title and genre are duplicates, will not add
            # them if they both are
            if(not session.query(exists().where(BookItem.title==title).where(BookItem.genre_id==thisGenre.id)).scalar()):
                newBook = BookItem(title=title, author=[author],
                description=desc,
                genre=thisGenre, imgURL=None, user_id=thisGenre.user_id)
                session.add(newBook)
                session.commit()
                thisBook = session.query(BookItem).filter_by(title=title).one()
                print(thisBook.title)
                flash(thisBook.title + " added!")
            else:
                thisBook = session.query(BookItem).filter_by(title=title).one()
                flash(thisBook.title + " already exists in your collection!")
            return redirect(url_for('viewPage', super_category_name=thisGenre.super_category.name, genre_id=thisBook.genre_id,
            book_id=thisBook.id))
        except:
            allGenres = session.query(Genre).all()
            return render_template('new-book.html', allGenres=allGenres)
    else:
        allGenres = session.query(Genre).all()
        return render_template('new-book.html', allGenres=allGenres)

# webpage that sets the imgURL property
# for a book
@app.route('/<string:super_category_name>/<int:genre_id>/<int:book_id>/cover_pic/<path:imgLocation>', methods=['POST'])
def setCoverImg(super_category_name, genre_id, book_id, imgLocation):
    thisBook = session.query(BookItem).filter_by(id = book_id).one()
    if(login_session['user_id']==thisBook.user_id and thisBook.imgURL==None): #verifies that the book belongs to the user who sent the POST request to set the image
        thisBook.imgURL = str(imgLocation)
        session.commit()
        return redirect(url_for('viewPage', API_KEY=CustomSearchAPIKEY, super_category_name=super_category_name, genre_id=genre_id, book_id=book_id))

# webpage that creates a new genre, with a form that uses POST to send the
# server a genre name and super-category the user enters
@app.route('/newgenre', methods=['GET', 'POST'])
def addGenre():
    if(request.method=='POST'):
        name = request.form['name']
        superCategoryName = request.form['category']
        user_id = login_session['user_id']
        superCategory = session.query(SuperCategory).filter_by(name=superCategoryName).one()
        newGenre = Genre(name=name, super_category=superCategory, user_id=user_id)
        session.add(newGenre)
        session.commit()
        flash(newGenre.name + " genre added!")
        allGenres = session.query(Genre).all()
        return render_template('new-book.html', allGenres=allGenres)
    else:
        superCategories = session.query(SuperCategory).all()
        return render_template('new-genre.html', allSuperCategories=superCategories)

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
