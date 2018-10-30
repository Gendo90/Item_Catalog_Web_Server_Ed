# Readme for "Best Books" website

## Intro

Hello! This website is used to help users keep track of books that they have
read or would like to read, and also hopefully introduce them to some new
favorites. This project uses the Flask framework to handle interactions
between back-end server code and front-end HTML, CSS, and JavaScript code, and
keeps track of information (e.g. books, genres, etc.) using SQLAlchemy's ORM
database functions. 

##---copied from earlier, full-stack project for structure/formatting!---


## Setup

This script and its functions are used to give plain text results to a user
for some basic database queries to the newspaper ('news') database. This
newspaper database must be located in the shared "vagrant" folder that is
made by unzipping the "FSND-Virtual-Machine" zip file provided by this course.
The newspaper database comes from the "newsdata.sql" file available [here][1].
This "newsdata.sql" database file must be located in the "vagrant"
folder mentioned above.

Once the "newsdata.sql" database file has been correctly extracted and placed,
the user needs to add the 'news' database to the Virtual Machine (VM). This
can be done first navigating to the "vagrant" folder on your computer, then
starting your VM by entering the command `vagrant up`. After the VM starts,
you need to login by entering the `vagrant ssh` command. Then you can enter
the command `psql -d news -f newsdata.sql`, which loads the database from
the "newsdata.sql" file into the VM and names the database there 'news'.


Next, the user needs to place this script (**news_queries_script.py**) into the
"vagrant" folder for it to run properly. Then you can navigate to the
**news_queries_script.py** file using the command line, located in the shared
"vagrant" folder. Once you find the directory containing the
**news_queries_script.py** file, you should enter
`python news_queries_script.py` to get the plain text results to the database
queries for the 'news' database, from the "newsdata.sql" database file. These
queries rank the most popular articles on the web site by number of views, the
most popular authors on the site by number of views of their articles, and the
dates when the percentage error of website loadings by visitors exceeded a
specified tolerance, which was 1% in this case.

### Example Usage

#### Popular Articles

The first example query gives the most popular articles on the website, ranked
by number of views by visitors. The code used to get this result in plain text
that a user can read is given as:
```
sql_raw_output = most_pop_articles()
format_pop_articles(sql_raw_output)
```
That code will print out a list of the most popular articles in order from
most- to least-viewed on the website, and will give you the number of views
per article.

#### Popular Authors

The second example query gives the most popular authors on the website, ranked
by number of views of their articles on the site by visitors. The code used to
get this result in plain text that a user can read is given as:
```
sql_raw_output = most_pop_authors()
format_pop_authors(sql_raw_output)
```
That code will print out a list of the most popular authors in order from
most visits to least visits to all their articles on the website, and will
give you the total number of visits for each author's body of work.

#### Failed Load Rate

The third example query checks the database 'logs' table for the number of
failed and correct loads of the website by visitors each day, and outputs the
date(s) when the percentage of failed loads of the website was greater than a
given error tolerance (1% in this case). The code that will give the date(s)
and the error rates for those dates that exceeds this tolerance in plain text
is given as:
```
test_dates, test_error, first_day, last_day = over_perc_error()
print_over_perc_err_dates(test_dates, test_error, first_day, last_day)
```
Which will give a clear, plain text printout of the dates and error rates that
a user can easily read. This code also gives the start and end dates for the
period of time that is examined for errors percentages that could be greater
than the given tolerance.

## Major Functions

### `most_pop_articles()`

Used to find the newspaper's most popular articles, determined by the number of
views by visitors to the website. The results include all the articles on the
website, ordered by views of each article.

### `most_pop_authors()`

Used to find the newspaper's most popular authors, determined from views of
their articles on the newspaper website. The authors are listed in order of
popularity, using their article views to rank them. The number of total views
of their articles on the newspaper website are also given for each author.

### `over_perc_error()`

Used to find the days when there was an unacceptable error rate for users
loading the website, which was 1% in this case. This function gives the dates
and the percentage error that exceeded the acceptable error rate. This error
rate is modifiable in the `check_perc_error()` sub-function that runs as part
of this `over_perc_error()` function. This function also prints the date range
that will be examined for unacceptable error rates.

## Minor/Supporting Functions

Here are some of the supporting functions and sub-functions, grouped by the
different purposes they serve and functions they can be used with.

### Formatting & Sub-Functions Functions for `most_pop_articles()`

#### `pop_articles_query_string()`

Used to store the query string that is used by the `most_pop_articles()`
function to query the news database and get the desired results in table form.
Returns the query string that is used with `most_pop_articles()` **execute**
statement.

#### `format_SQL_output()`

Used to split an input list of tuples that represent values from the SQL table
that share the same row and have different columns into two lists that
represent the values of the columns in the same order with the same length.

#### `format_pop_articles()`

This function gets as input the two lists made by `format_SQL_output()` from
the SQL list of tuples that was the output of `most_pop_articles()`, because
those lists represent the columns from that table with values for the article
names and the number of views of each article. This function formats those
results into plain text that a human user can understand.

### Formatting Functions & Sub-Functions for `most_pop_authors()`

#### `pop_authors_query_string()`

Used to store the query string that is used by the `most_pop_authors()`
function to query the news database and get the desired results in table form.
Returns the query string that is used with `most_pop_authors()` **execute**
statement. Also uses the `pop_articles_query_string()` as a building-block for
its own query string, with a variable name replaced due to a similar name.

#### `format_SQL_output()`

Used to split an input list of tuples that represent values from the SQL table
that share the same row and have different columns into two lists that
represent the values of the columns in the same order with the same length.

#### `format_pop_authors()`

This function gets as input the two lists made by `format_SQL_output()` from
the SQL list of tuples that was the output of `most_pop_authors()`, because
those lists represent the columns from that table with values for the author
names and the number of views of each author's work. This function formats
those results into plain text that a human user can understand.

### Formatting & Sub-Functions for `over_perc_error()`

#### Sub-Function: `make_loaded_by_date_table()`

Queries the SQL 'news' database to find the dates, number of erroneous loads of
the website, and number of correct loads of the website. Outputs this
information as a list containing each row as a tuple.

#### Sub-Function: `check_perc_error()`

Takes in the list of tuples from the output of the `make_loaded_by_date_table()`
and determines which dates had unacceptable error rates, given a certain
error percentage (1% in this case, defined in this function as the variable
perc_err_threshold). The function compares the number of erroneous loads to the
total number of loads to get this actual error percentage rate. The output is
two lists that represent the date and the error percentage that was over the
limit, and two dates that represent the first and last date the website
loadings were examined, to provide a date range as context.

#### Formatting: `print_over_perc_err_dates()`

This function gets as input the two lists output by `over_perc_error()` that
represent the dates when the percentage error in loadings was too high,
and what that percentage was for those dates. It also gets the output dates
from the `over_perc_error()` function because they give the date range over
which the percentage errors were examined for each day. This function
formats all these results into plain text that a human user can understand.

[1]: /newsdata.sql
