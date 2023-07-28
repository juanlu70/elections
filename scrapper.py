#!/usr/bin/env python3

import json
import random
import scraping
import argparse

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import Session


class ManageScraper:
    def __init__(self):
        self.follow_up = 1
        self.tlist = None
        self.regions = []
        self.provinces = []
        self.towns_file = "towns.json"
        self.towns_urls = []
        self.scraped = []

        # -- functions to initialize and fill all variables --
        self.process_arguments()
        self.open_towns_file()
        self.fill_regions()
        self.fill_provinces()
        self.get_towns()
        self.get_towns_track()

        return

    # -- open regions/provinces/towns file --
    def open_towns_file(self) -> None:
        """
        Open towns file and put data on town list

        :return: None
        """
        fp = open(self.towns_file, "r")
        poblaciones = fp.read()
        fp.close()

        self.tlist = json.loads(poblaciones)

        return

    # -- fill regions list --
    def fill_regions(self) -> None:
        """
        Fill the regions list from dict number 1 of towns file

        :return: None
        """
        for item in self.tlist[1]['list']:
            region = {
                'region': item['n'],
                'code': str(item['c'])
            }
            self.regions.append(region)

        return

    # -- get region name by code --
    def get_region(self, code: str) -> str:
        """
        Get a region name with region code

        :param code: str
        :return: str
        """
        result = ""

        for item in self.regions:
            if item['code'] == code:
                result = item['region']

        return result

    # -- fill provinces list --
    def fill_provinces(self) -> None:
        """
        Fill the provinces list from dict number 2 of towns file

        :return: None
        """
        for item in self.tlist[2]['list']:
            province = {
                'province': item['n'],
                'code': str(item['c'])
            }
            self.provinces.append(province)

        return

    # -- get province name by code --
    def get_province(self, code: str) -> str:
        """
        Get a province name with the province code

        :param code: str
        :return: str
        """
        result = ""

        for item in self.provinces:
            if item['code'] == code:
                result = item['province']

        return result

    # -- get towns already download for continue with already not download --
    def get_towns_track(self) -> None:
        engine = create_engine("mysql://juanlu@127.0.0.1/elections")
        conn = engine.connect()

        # -- delete last town because it was the source of error --
        results = conn.execute(text("SELECT MAX(id) FROM towns;"))
        last_id = results.first()[0]
        conn.execute(text("DELETE FROM towns WHERE id="+str(last_id)))
        conn.commit()

        # -- get all towns in DB --
        results = conn.execute(text("SELECT town FROM towns;"))
        for town in results.mappings():
            self.scraped.append(town['town'])

        return

    # -- this function opens towns file to get the URLs for scraping loop --
    def get_towns(self) -> None:
        """
        Fill the towns list with dict 3 of towns file

        :return: None
        """
        # -- fill list with all towns with parameters --
        for pob in self.tlist[4]['list']:
            cod_one = str(pob['i'])
            cod_two = str(pob['l'])

            town = {
                'id': 0,
                'town': pob['n'].replace("'", "\\'"),
                'region': self.get_region(pob['20']).replace("'", "\\'"),
                'province': self.get_province(pob['30']).replace("'", "\\'"),
                'url': "https://resultados.locales2023.es/resultados/0/"+cod_one+"/"+cod_two
            }
            self.towns_urls.append(town)

        return

    # --

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
        for url in range(0, len(self.towns_urls)):
            item = random.randint(0, len(self.towns_urls) -1)
            if item not in self.scraped:
                town = self.towns_urls[item]

                # -- save town to db to take track --
                sqlsession.execute(text("INSERT INTO towns (town, province, region) VALUES ('"+town['town']+"', '" +
                                        town['province']+"', '"+town['region']+"');"))
                sqlsession.commit()
                result = sqlsession.execute(text("SELECT id FROM towns WHERE town='"+town['town']+"';"))
                town['id'] = result.first()[0]
                self.scraped.append(town['town'])

                # -- get page from 2023 results --
                data = scrap.scrape_url(self.towns_urls[item])

                # -- get results from page --
                results = scrap.get_data(self.towns_urls[item], data)

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
                            help="Remove old scrapping and begin again with all towns")
        args = parser.parse_args()

        if args.remove == 1:
            self.follow_up = 0

        return


if __name__ == "__main__":
    """
    Main function, initialize and start scraping loop
    """
    mscrap = ManageScraper()
    scrap = scraping.Scraping()

    # -- if got remove flag, delete entire database --
    if mscrap.follow_up == 0:
        mscrap.delete_db()

    # -- normal scraping process --
    mscrap.make_scrapping()
