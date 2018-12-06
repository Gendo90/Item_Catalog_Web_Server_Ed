# Server Configuration of www.bestbookcollection.com

## Overview

Hello! This document is intended to explain the server configuration for the
website at www.bestbookcollection.com. The website itself uses the Flask web
development framework and the SQLAlchemy ORM to flexibly execute and manage
the website as it grows, and the web application itself is hosted on a remote
Ubuntu Linux server as a WSGI app with the Apache HTTP server software. The
SQLAlchemy ORM connects to a PostgreSQL database on the Ubuntu server to
store and retrieve the data used to populate the website with books. Finally,
some online, third-party "cloud" resources were used to make this website,
including Amazon Lightsail and CloudFront, Facebook Oauth 2.0 login, and
Google Oauth 2.0 login and custom search API, which will be explained later
in more detail **[HERE!!!!!!!!!!!]**.

## Server Configuration

The server is an Amazon Web Services Lightsail instance, so it is technically
part of the "cloud," and runs the Ubuntu 18.04 LTS version of the Linux
Operating System (OS). The server is available at the following static IP
address: 52.39.137.28. However, if a user tries to access the website using
that IP address in their browser, they will not be able to login to the site
because the URL connected to that IP address is not validated for the Google
or Facebook Oauth 2.0 logins. Instead, the user would need to access the
website at https://www.bestbookcollection.com to log in and access theirs and
others' book collections. On the other hand, that IP Address **must** be used
to access the Ubuntu server for maintenance, upgrades, etc.

The two valid users for remote logins on the Ubuntu server are `ubuntu` and
`grader`. There is another `root` user - as is standard for Linux - but that
account cannot be logged into remotely to prevent intruders on the server from
gaining access and permissions to all the folders and files on it. This remote
access to `root` was disabled by changing the value of 'yes' for
'PermitRootLogin' to 'no' in the `/etc/ssh/sshd_config` file on the server.
Both users `ubuntu` and `grader` are given `sudo` privileges on the server,
so they can both make changes to root files and folders. They were granted
these privileges by adding the correct files to `/etc/sudoers.d` on the
server.

The server has been configured so that it has a firewall blocking all ports
except for `SSH` (port 2200), `HTTP` (port 80), and `NTP` (port 123). The
firewall used was the built-in "Uncomplicated Firewall" (`ufw`), and it was
set to deny all incoming - other than the ports already mentioned - and allow
all outgoing.

You might note that `SSH` has been changed from the standard port of 22 to the
non-standard port of 2200 - this change was made as the specifications
require. This change of ports was enacted by setting the "Port" number to
2200 in the `/etc/ssh/sshd_config` file on the server. Key-based login was
also enforced by modifying that same file so that the value given for
'PasswordAuthentication' was changed from 'yes' to 'no'.

Finally, the software on the server is kept current by running the following
commands if the Ubuntu login screen shows that packages could be updated. The
first command is `sudo apt-get update`, which updates the server's information
about different versions of software available for packages already installed.
The second command is `sudo apt-get upgrade` to install core packages. The
third command is `sudo apt-get dist-upgrade` to install packages for
applications not included on the base Ubuntu install image.


## Software Installed on Server


## Third Party Resources


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

### API's Available

#### Book JSON

Each book has a JSON endpoint that gives the same information as the book
viewer webpage. A user can access this JSON information by navigating to
nearly the same path as the book viewer, they would just replace the "view"
part of the path with "JSON" For example, if a user wanted to retrieve the
JSON information for a book with id=9, genre="Fantasy", and
superCategory="Fiction", they would be able to view the book at
http://localhost:8000/Fiction/Fantasy/9/view and to get the desired JSON
information, they would need to replace the "view" with "JSON" as mentioned
earlier, so they would navigate to http://localhost:8000/Fiction/Fantasy/9/JSON
This path structure should work with all books in the catalog.

#### Genre JSON

Each genre has a JSON endpoint as well, that gives information about all the
books within it. The genres are categorized by their names, so you would
navigate to the webpage to view all the books in a given genre (e.g.
http://localhost:8000/Fiction/Fantasy/) and then append "JSON" on the end of
that path to retrieve the JSON information for that entire genre. For example,
to get all the books contained within the "Fantasy" genre listed in a single
JSON file, you could navigate to http://localhost:8000/Fiction/Fantasy/JSON
This path structure should work with all genres in the catalog, and will
show you books from different users in the same genre and duplicate books
in a given genre as well.

#### SuperCategory JSON

Each SuperCategory has a JSON endpoint that gives information about all the
genres within it. The SuperCategories are categorized by their names, so you
would navigate to the webpage to view all the genres in a given SuperCategory
(e.g. http://localhost:8000/Fiction/) and then append "JSON" on the end of
that path to retrieve the JSON information for that entire SuperCategory. For
example, to get all the genres contained within the "Fiction" SuperCategory
listed in a single JSON file, you could navigate to
http://localhost:8000/Fiction/JSON This path structure should work with all
three SuperCategories in the catalog, and will show you genres from different
users and list each genre name once (no duplicates in the JSON file even if
multiple users added the same genre and they are technically different in the
database).

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

[1]: https://github.com/udacity/fullstack-nanodegree-vm
[2]: http://localhost:8000
[3]: application.py
[4]: preload_booklist_with_users.py
[5]:
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates
[6]: http://exploreflask.com/en/latest/static.html
