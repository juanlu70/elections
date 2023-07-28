import time
import json

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By


class Scraping:
    def __init__(self):
        self.year = "2023"
        self.chromedriver_path = "/usr/local/bin/chromedriver"

        return

    # -- scrape a URL from town data --
    def scrape_url(self, town: dict) -> dict:
        """
        Get the URL from dict and scrape the town page
        then process page to find all results from am
        injected JSON.

        :param town: dict
        :return: dict
        """
        # -- hide the display of selenium browser --
        display = Display(visible=0, size=(800, 600))
        display.start()

        # -- create chrome webdriver for selenium --
        options = webdriver.ChromeOptions()
        service = ChromeService(executable_path=self.chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)

        # -- download page URL 2023 --
        print("Getting town "+town['town']+" ("+town['province']+"-"+town['region']+") from "+town['url']+"...")
        driver.get(town['url'])
        time.sleep(3)

        # -- extract JSON from page with results --
        data = driver.find_element(By.ID, '__NEXT_DATA__').get_attribute('innerHTML')
        tmp = json.loads(data)
        data_json = tmp['props']['pageProps']['ScopeResponse']['scope']

        # -- save data to disk and close selenium --
        fp = open("datos/"+town['town'].replace("/", "-")+"-"+self.year+".html", "w")
        fp.write(data)
        fp.close()

        driver.quit()
        display.stop()

        return data_json

    # -- compose database data from the town JSON data for 2023 and 2019 --
    def get_data(self, town: dict, data: dict) -> dict:
        # -- process elections data --
        all_results = {
            'elections': [{
                'town_id': town['id'],
                'year': 2023,
                'election_type': "municipales",
                'census': data['censoINE'],
                'participation': data['escrutinio']['participacion']['def'],
                'abstention': data['escrutinio']['porcAbstencion']['def'],
                'totalvotes': data['escrutinio']['votosTotales']['def'],
                'nullvotes': data['escrutinio']['votosNulos']['def'],
                'emptyvotes': data['escrutinio']['votosBlancos']['def'],
                'validvotes': data['escrutinio']['votosValidos']['def']
            }, {
                'town_id': town['id'],
                'year': 2019,
                'election_type': "municipales",
                'census': data['escrutinioAnt'][0]['censoEscrutado']['def'],
                'participation': data['escrutinioAnt'][0]['participacion']['def'],
                'abstention': data['escrutinioAnt'][0]['porcAbstencion']['def'],
                'totalvotes': data['escrutinioAnt'][0]['votosTotales']['def'],
                'nullvotes': data['escrutinioAnt'][0]['votosNulos']['def'],
                'emptyvotes': data['escrutinioAnt'][0]['votosBlancos']['def'],
                'validvotes': data['escrutinioAnt'][0]['votosValidos']['def']
            }],
            'results': [],
        }

        # -- process party results data 2023 --
        results = []
        for item in data['escrutinio']['partidos']:
            party = {
                'town_id': town['id'],
                'year': 2023,
                'election_type': "municipales",
                'party': item['siglas'].replace("'", "\\'"),
                'votes': item['votos']['def'],
                'percentage': item['porcentaje']['def']
            }
            results.append(party)

        # -- process party results data 2019 --
        for item in data['escrutinioAnt'][0]['partidos']:
            party = {
                'town_id': town['id'],
                'year': 2019,
                'election_type': "municipales",
                'party': item['siglas'].replace("'", "\\'"),
                'votes': item['votos']['def'],
                'percentage': item['porcentaje']['def']
            }
            results.append(party)

        all_results['results'] = results

        return all_results
