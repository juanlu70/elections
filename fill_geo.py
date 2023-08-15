import json
import random


class FillGeo:
    def __init__(self):
        self.tlist = None
        self.regions = []
        self.provinces = []
        self.towns_file = "towns_locals.json"
        self.towns_urls = []
        self.scraped = []

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
        Get a region name with region code as input

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
        Get a province name with the province code as input

        :param code: str
        :return: str
        """
        result = ""

        for item in self.provinces:
            if item['code'] == code:
                result = item['province']

        return result

    # -- this function opens towns file to get the URLs for scraping loop --
    def fill_towns(self, election_type: str) -> None:
        """
        Fill the towns list with dict 3 of towns file

        :return: None
        """
        # -- fill list with all towns with parameters --
        for town in self.tlist[4]['list']:
            cod_one = str(town['i'])
            url = ""
            url_alt = ""

            if election_type == "locals":
                cod_two = str(town['l'])
                url = "https://resultados.locales2023.es/resultados/0/"+cod_one+"/"+cod_two
                url_alt = ""
            if election_type == "generals":
                code = str(town['c'])
                url = "https://resultados.generales23j.es/backend-difu/scope/data/getScopeData/"+code+"/1/2/1/0"
                url_alt = "https://resultados.generales23j.es/backend-difu/scope/data/getScopeData/"+code+"/2/3/1/0"

            town = {
                'id': 0,
                'town': town['n'].replace("'", "\\'"),
                'region': self.get_region(town['20']),
                'province': self.get_province(town['30']),
                'url': url,
                'url_alt': url_alt
            }
            self.towns_urls.append(town)

        return

    # -- get a random town still not processed --
    def get_town(self) -> dict:
        town = {}

        for url in range(0, len(self.towns_urls)):
            item = random.randint(0, len(self.towns_urls)-1)
            tmp_town = self.towns_urls[item]
            if tmp_town['town'] not in self.scraped:
                town = tmp_town

        if town == {}:
            town = {'town': "end"}

        return town

    # -- main function to make all the fill process --
    def main(self, election_type: str) -> None:
        self.open_towns_file()
        self.fill_regions()
        self.fill_provinces()
        self.fill_towns(election_type)

        return
