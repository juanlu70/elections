# ELECTIONS

This program is a demonstration of how I can manage a project.

The purpose is to compare Spain's 2023 local election results with 
2023 Parlament elections results and to get some stats or maybe detect
some fake results (if any).


# PROGRAM FLOW

The program is planned to make a scraping of the local 2023-2019 election
results and store itr on a database from https://resultados.locales2023.es/

At the time of writing this document there is a scrape program already done 
that get results from local elections of 2019 and 2023 using Selenium and
SQLAlchemy.

The database comes empty and only with the schema for MySQL/MariaDB.


# FUTURE PROGRAM ADDINGS

The plan is to add another scraper for 2023 parlamentary elections and
2019 too if available.

Then make a further table for calculations in every town of the list to
add comparison numbers, comparing census, votes, empty votes and many
other numbers.

Then make an API point for export the results, likely including the results
by town because in Spain there is not an API point with elections results
(terrific but true).


# INSTALLATION

1.- You must add the python libraries for the program with:

pip3 install -r requirements.txt

2.- The program is done for Linux/Unix systems, but could need some modification
to run in Windows, specially on path definitions.

Also you have to install xvfb, on Ubuntu:

apt install xvfb

3.- Create the MySQL/MariaDB database "elections" and give permission to some user.

Then add the dump to create the database schema with tables and indexes:

mysql elections < elections-schema.sql


# EXECUTION

Once the libraries are installed you only need to execute the program:

./scrapper.py

If the program stops for any reason it will resume the scraping at the same point.

If you want to remove all database and start again you have to execute with flag -r:

./scrapper.py -r

This will delete all tables and will start the process again.


