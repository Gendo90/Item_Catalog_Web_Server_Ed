# Readme for "Best Books" website

## Intro

Hello! This website is used to help users keep track of books that they have
read or would like to read, and also hopefully introduce them to some new
favorites. This project uses the Flask framework to handle interactions
between back-end server code and front-end HTML, CSS, and JavaScript code, and
keeps track of information (e.g. books, genres, etc.) using SQLAlchemy's ORM
database methods.

## Setup

This website is run from the "[application.py][1]" python script which acts as
the "server" or back-end application. You can run this directly without
creating a script to load the database with information first, but it is
recommended that you create and run a script similar to
"[preload_booklist_with_users.py][2]" so that the "booklistwithusers.db" is
created **before** running the server and is populated with some books and
their descriptions, genres, etc. You could make the entries with the user_id
set to 1, which signifies the first user of the website, which would be
**you**, assuming you login before anyone else. If you decide not to create a
script to load all your books and genres into the website's database, the main
page of the website will load only the three main "SuperCategory" entries into
the database (e.g. "Fiction", "Non-Fiction", and "Reference") when accessed,
without any genres or books for any users. Thus, you would need to manually
add all the genres and books you want for yourself, because the database is
empty other than those three SuperCategory entities.

Regardless of whether or not a database is created before running the
"[application.py][1]" server script, the script should be run from the command
line by entering the `python application.py` command after having navigated to
the directory containing the "[application.py][1]" file. The directory
structure is highly rigid for this application, because the Flask framework
requires certain folders to be named "templates" and "static", so the server
may not work correctly if any of the files in these folders are moved, or
deleted, so please maintain the directory structure as it is given to ensure
the server works properly. You can learn more about this requirement in Flask
[here for templates][3] and [here for static files][4].

After running the `python application.py` command, you should be able to access
the website application at the "localhost:8000" address in a browser. Login is
required for adding, editing, or deleting books or genres and each user can
only change their own books that they have entered at this time after logging
in to their account. Users currently have two options for logging into the
website, because they can verify their identities and get access to their
account using either their Google or Facebook login credentials.


### Example Usage

#### Login

The user can login from the main page of the website, accessible at
"localhost:8000", by clicking on the "Login" button on the right side of the
header. This button will bring the user to a page where they can select to
login using either their Google or their Facebook account. Once they have
successfully logged in using one of these accounts, the page will change to
show their profile picture and let them know that they have logged in
successfully, and then will redirect to the main page of the website. The user
will now have access to their books and genres and the capability to add more
books and genres to their account. The "Login" button on the right side of the
header will be replaced with a "Logout" button.

#### Add A Genre

Users who are logged in can add genres to the website, and will be able to view
their own genres and other users' genres. The buttons to add new genres are
located near the top of the sidebar on the "genreIndex.html" webpage, and also
on the "new-book.html" webpage so that a user can easily add a new genre before
adding a book to that genre, since the genre must exist before a book of that
genre may be added.

Genres are removed when they are empty and upon the user who deleted the last
books in the genre logging out - that is, if all books in a particular genre
have been deleted by the user, and they were the last remaining books in that
genre so that it is now empty, the genre will be removed from the database
when the user decides to log out. This deletion upon logout means that a user
can add books to empty genres after newly creating a genre, and that they could
add different books to genres that they removed all the books from in the same
login session, so it adds flexibility to the user experience while also
streamlining CRUD operations.

#### Add A Book

A user may add a book to their collection when logged into the website. They
can add a book by entering its title, author(s), genre, and description into
the form on the "new-book.html" webpage, which also has a path defined by the
Flask decorator as "/newbook" After adding a book, the website notifies the
user that a book has been successfully added using a "flash" message and
redirects to the page on which to view the book.

#### Edit A Book

A user may edit a book in their collection when logged into the website. The
user should navigate to the view page for the book that they would like to
edit after logging in, and then press the "Edit" button. This will allow the
user to edit their description and notes for a given book, on the same view
page. After editing a book's description, the website will redirect to the
same book view page, with the new, updated description shown.

#### Remove A Book

A user may remove a book in their collection when logged into the website. The
user should navigate to the view page for the book that they would like to
edit after logging in, and then press the "Delete" button. A confirmation
window will appear asking if the user would really like to delete the book
from their collection, and the options are "Ok" or "Cancel" - if the user
selects "Ok", the book is deleted, and if they select "Cancel", the
confirmation window disappears and nothing happens (i.e. the book is not
removed).

#### Logout

Logout is one of the easiest actions to take using this app - a user who is
already logged in just clicks on the "Logout" button at the right end of the
website header, and the website will log the user out from their session on
this website. Just as a reminder, the website uses Google and Facebook
accounts for authorization, so they would need to log back in using one of
these providers if they want to add, edit, or delete their books on the
website again.


## Planned Features/Current Limitations

A planned, upcoming feature is the ability to view random selections of other
users' books, based on genre names that match genres in your personal
collection, as well as some random books that will be featured on the public
area of the website for any site visitors.

Soon you will be able to view books and genres **only** in your collection and
nothing from any other user's collection by following a "My Collection" link
when logged in!

There will also be a footer added to the website displaying information like
contact information, year(s) during which the website was developed and
maintained, and possibly some quick links to pages like the home page and the
"My Collection" pages and possibly recently visited pages on the site.

Another planned upgrade would allow more books to be added each day, while
enabling a revenue stream as an Amazon Associate. This upgrade consists of
replacing the Google Custom Search API currently used to find book cover
images with an Amazon API that returns images for their book products. This
restricts the image search work only when locating products that Amazon has,
but their product database is extensive, so most books can be found without any
issues. As a benefit, however, this upgrade would allow unlimited image
searches every day, and could generate income for the website from purchases
made by users referred to Amazon through a link to the book attached to the
book image. The unlimited image searches per day would be a huge improvement
over the current Google Custom Search API which allows up to **100 searches
for free** before paying them to allow more searches. Google's Custom Search
API was used during development because it is easier to access than Amazon's
Associate APIs, since the website needs a formal address to even register as
an Amazon Associate. The documentation from Google is more comprehensive and
makes their API easier to implement as well.

[1]: application.py
[2]: preload_booklist_with_users.py
[3]:
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates
[4]: http://exploreflask.com/en/latest/static.html
