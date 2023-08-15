#!/usr/bin/env python3

import random
import argparse
import fill_geo
import scraping

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import Session


scrap = scraping.Scraping()
geo = fill_geo.FillGeo()


class ManageScraper:
    def __init__(self):
        self.scope = ""

        return

    # -- get towns already download for continue with already not download --
    def get_towns_track(self) -> None:
        engine = create_engine("mysql://juanlu@127.0.0.1/elections")
        conn = engine.connect()

        # -- delete last town because it was the source of error --
        results = conn.execute(text("SELECT MAX(id) FROM towns WHERE locals=True;"))
        last_id = results.first()[0]

        if last_id is not None:
            conn.execute(text("DELETE FROM towns WHERE id="+str(last_id)))
            conn.commit()

        # -- get all towns in DB --
        results = conn.execute(text("SELECT town FROM towns WHERE locals=True;"))
        for town in results.mappings():
            geo.scraped.append(town['town'])

        return

    # -- insert into db --
    def insert_into_db(self, dbsession: Session, data: dict) -> None:
        """
        Function to insert elections and results into database.

        :param dbsession: Sqlalchemy session
        :param data: dict
        :return: None
        """
        # -- save election rows --
        for item in data['elections']:
            query = ("INSERT INTO elections " +
                     "(town_id, year, election_type, census, participation, abstention, totalvotes, nullvotes, " +
                     "emptyvotes, validvotes) VALUES (")
            for value in item.keys():
                query += "'" + str(item[value]) + "',"
            query = query[0:-1]
            query += ");"

            dbsession.execute(text(query))

        # -- save results rows --
        for item in data['results']:
            query = "INSERT INTO results (town_id,year,election_type,party,votes,percentage) VALUES ("
            for value in item.keys():
                query += "'" + str(item[value]) + "',"
            query = query[0:-1]
            query += ");"

            dbsession.execute(text(query))

        dbsession.commit()

        return

    # -- scrap all pages in random order and store in database --
    def make_scrapping(self):
        """
        Random loop on towns without repeat it
        to get all towns data and insert into DB.

        :return: None
        """
        # -- initialize sqlalchemy --
        engine = create_engine("mysql://juanlu@127.0.0.1/elections")
        sqlsession = Session(engine)

        # -- loop for towns --
        for row in range(0, len(geo.towns_urls)):
            town = geo.get_town()

            # -- save town to db to take track --
            sqlsession.execute(text("INSERT INTO towns (town, locals, congreso, senado, province, region) " +
                                    "VALUES ('"+town['town']+"', True, False, False, '"+town['province']+"', '" +
                                    town['region']+"');"))
            sqlsession.commit()
            result = sqlsession.execute(text("SELECT id FROM towns WHERE town='"+town['town']+"' AND locals=True;"))
            town['id'] = result.first()[0]
            geo.scraped.append(town['town'])

            # -- get page result --
            data = scrap.scrape_url_locals(town)

            # -- get results from page --
            results = scrap.get_data_locals(town, data)

            # -- insert into db --
            self.insert_into_db(sqlsession, results)

        return

    # -- delete all tables --
    def delete_db(self) -> None:
        """
        Function to delete all tables when flag --remove is added to command-line
        """
        print("Deleting tables...")

        query_list = [
            "DELETE FROM elections;",
            "DELETE FROM results;",
            "DELETE FROM towns;"
        ]

        engine = create_engine("mysql://juanlu@127.0.0.1/elections")
        conn = engine.connect()

        for query in query_list:
            conn.execute(text(query))
        conn.commit()

        return

    # -- process command line arguments --
    def process_arguments(self) -> None:
        """
        Function to process command-line arguments
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-r", "--remove", action="count", default=0,
                            help="Remove old scrapping and begin again.")
        args = parser.parse_args()

        if args.remove == 1:
            self.delete_db()

        return

    # -- main function --
    def main(self) -> None:
        """
        Function to head the program flow

        :return: None
        """
        self.process_arguments()
        geo.main(self.scope)
        self.get_towns_track()
        self.make_scrapping()

        return


if __name__ == "__main__":
    """
    Start program
    """
    mscrap = ManageScraper()
    mscrap.scope = "locals"
    mscrap.main()
