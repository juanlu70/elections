# Elections

This program is a demonstration of how I can manage a project.

The purpose of this project is to compare Spain's 2023 local elections results with 2023 Parlament elections results 
and to get some stats or maybe detect some fake results (if any) and to set an API point for the results because
spanish government seems to don't care about making this important information public.


# Program flow

The program is planned to make a scraping of the local 2023-2019 election results and store it on a database 
from https://resultados.locales2023.es/ this scraper is scraper_locals.py.

Now the Congreso/Senado 2023-2019 election results (where it is available) and store it on the database from
https://resultados.generales23j.es/ this scraper is scraper_generals.py, this part is under current development. 

At the time of writing this document both scrapers programs are done local elections scraper works with Selenium,
general elections work with only requests library and both and SQLAlchemy.

The database comes empty and only with the schema for MySQL/MariaDB.


# Future program addings

The plan is to finish general elections scraper, to add a calculation script by town and to add a FastAPI API point 
to query results and calculated results.


# Installation

1- You must add the python libraries for the program with:

pip3 install -r requirements.txt

2- The program is done for Linux/Unix systems, but could need some modification to run in Windows, specially on path 
definitions.

Also, you have to install xvfb, on Ubuntu:

apt install xvfb

3 Create the MySQL/MariaDB database "elections" and give permission to some user.

Then add the dump to create the database schema with tables and indexes:

mysql elections < elections-schema.sql

This program is not made for Windows, I am sorry, but I don't like "buggy" operating systems, however it must be simple
to adapt.


# Execution

Once the libraries are installed you only need to execute the program for local elections:

./scrapper_locals.py

Or general elections:

./scrapper_generals.py

If the program stops for any reason it will resume the scraping at the same point.

If you want to remove all database and start again you have to execute with flag -r:

./scrapper_locals.py -r

or

./scrapper_generals.py -r

This will delete all tables and will start the process again.


# Tests

There are tests for checking almost all functions (this part is under development)
