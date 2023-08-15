import time
import json
import requests
import selenium

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By


class Scraping:
    def __init__(self):
        self.year = "2023"
        self.data_dir = "data/"
        self.chromedriver_path = "/usr/local/bin/chromedriver"

        return

    # -- scrape a locals URL from town data --
    def scrape_url_locals(self, town: dict) -> dict:
        """
        Get the URL from dict for and scrape the town page
        then process page to find all results from am
        injected JSON from local elections

        :param town: dict
        :return: dict
        """
        # -- hide the display of selenium browser --
        display = Display(visible=False, size=(800, 600))
        display.start()

        # -- create chrome webdriver for selenium --
        options = webdriver.ChromeOptions()
        service = ChromeService(executable_path=self.chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)

        # -- download page URL 2023 --
        print("Getting town "+town['town']+" ("+town['province']+"-"+town['region']+") from "+town['url']+"...")
        driver.get(town['url'])
        time.sleep(3)
        result = requests.get(town['url'])

        # -- extract JSON from page with results --
        try:
            data = driver.find_element(By.ID, '__NEXT_DATA__').get_attribute('innerHTML')
        except selenium.common.exceptions.NoSuchElementException:
            time.sleep(10)
            print("Retrying town " + town['town'] + " (" + town['province'] + "-" + town['region'] + ") from " +
                  town['url'] + "...")
            driver.get(town['url'])
        time.sleep(3)

        data = driver.find_element(By.ID, '__NEXT_DATA__').get_attribute('innerHTML')
        tmp = json.loads(data)
        data_json = tmp['props']['pageProps']['ScopeResponse']['scope']

        # -- save data to disk and close selenium --
        fp = open(self.data_dir+town['town'].replace("/", "-")+"-"+self.year+".html", "w")
        fp.write(json.dumps(data))
        fp.close()

        driver.quit()
        display.stop()

        return data_json

    # -- compose database data from the town JSON data for 2023 and 2019 --
    def get_data_locals(self, town: dict, data: dict) -> dict:
        # -- process elections data --
        all_results = {
            'elections': [{
                'town_id': town['id'],
                'year': 2023,
                'election_type': "locals",
                'census': data['censoINE'],
                'participation': data['escrutinio']['participacion']['def'],
                'abstention': data['escrutinio']['porcAbstencion']['def'],
                'totalvotes': data['escrutinio']['votosTotales']['def'],
                'nullvotes': data['escrutinio']['votosNulos']['def'],
                'emptyvotes': data['escrutinio']['votosBlancos']['def'],
                'validvotes': data['escrutinio']['votosValidos']['def']
            }],
            'results': []
        }

        # -- sometimes escrutinioAnt is null --
        census = 0
        participation = 0
        abstention = 0.00
        totalvotes = 0
        nullvotes = 0
        emptyvotes = 0
        validvotes = 0

        if 'escrutinioAnt' in data and data['escrutinioAnt'] is not None:
            census = data['escrutinioAnt'][0]['censoEscrutado']['def']
            participation = data['escrutinioAnt'][0]['participacion']['def']
            abstention = data['escrutinioAnt'][0]['porcAbstencion']['def']
            totalvotes = data['escrutinioAnt'][0]['votosTotales']['def']
            nullvotes = data['escrutinioAnt'][0]['votosNulos']['def']
            emptyvotes = data['escrutinioAnt'][0]['votosBlancos']['def']
            validvotes = data['escrutinioAnt'][0]['votosValidos']['def']

        all_results['elections'].append({
            'town_id': town['id'],
            'year': 2019,
            'election_type': "locals",
            'census': census,
            'participation': participation,
            'abstention': abstention,
            'totalvotes': totalvotes,
            'nullvotes': nullvotes,
            'emptyvotes': emptyvotes,
            'validvotes': validvotes
        })

        # -- process party results data 2023 --
        results = []

        if 'partidos' in data['escrutinio']:
            for item in data['escrutinio']['partidos']:
                party = {
                    'town_id': town['id'],
                    'year': 2023,
                    'election_type': "locals",
                    'party': item['siglas'].replace("'", "\\'"),
                    'votes': item['votos']['def'],
                    'percentage': item['porcentaje']['def']
                }
                results.append(party)

        # -- process party results data 2019 --
        if 'escrutinioAnt' in data:
            if data['escrutinioAnt'] is not None:
                for item in data['escrutinioAnt'][0]['partidos']:
                    party = {
                        'town_id': town['id'],
                        'year': 2019,
                        'election_type': "locals",
                        'party': item['siglas'].replace("'", "\\'"),
                        'votes': item['votos']['def'],
                        'percentage': item['porcentaje']['def']
                    }
                    results.append(party)

        all_results['results'] = results

        return all_results

    # -- scrape generals URLS from town data --
    def scrape_url_generals(self, town: dict) -> list:
        """
        Get the URL from dict for and scrape the town page
        then process page to find all results from a
        JSON from generals elections

        :param town: dict
        :return: dict
        """
        data = []

        print("Getting town "+town['town']+" ("+town['province']+"/"+town['region']+" from "+town['url']+"...")

        result = requests.get(town['url'])
        data.append(result.json())
        result = requests.get(town['url_alt'])
        data.append(result.json())

        # -- save result to file --
        fp = open(self.data_dir+town['town'].replace("/", "-")+"_generals.json", "w")
        fp.write(json.dumps(data))
        fp.close()

        return data

    def get_data_generals(self, town: dict, data: list) -> dict:
        results = {}

        print("DATA:")
        print(data)
        print("-----------------------------------------------")

        # -- process elections data (congreso) --
        all_results = {
            'congreso': [{
                'town_id': town['id'],
                'year': 2023,
                'election_type': "congreso",
                'census': data[0]['scope']['censoINE'],
                'participation': data[0]['scope']['escrutinio']['participacion']['def'],
                'abstention': data[0]['scope']['escrutinio']['porcAbstencion']['def'],
                'totalvotes': data[0]['scope']['escrutinio']['votosTotales']['def'],
                'nullvotes': data[0]['scope']['escrutinio']['votosNulos']['def'],
                'emptyvotes': data[0]['scope']['escrutinio']['votosBlancos']['def'],
                'validvotes': data[0]['scope']['escrutinio']['votosValidos']['def'],
                'results': []
            }, {
                'town_id': town['id'],
                'year': 2019,
                'election_type': "congreso",
                'census': data[0]['scope']['censoINE'],
                'participation': data[0]['scope']['escrutinioAnt'][0]['participacion']['def'],
                'abstention': data[0]['scope']['escrutinioAnt'][0]['porcAbstencion']['def'],
                'totalvotes': data[0]['scope']['escrutinioAnt'][0]['votosTotales']['def'],
                'nullvotes': data[0]['scope']['escrutinioAnt'][0]['votosNulos']['def'],
                'emptyvotes': data[0]['scope']['escrutinioAnt'][0]['votosBlancos']['def'],
                'validvotes': data[0]['scope']['escrutinioAnt'][0]['votosValidos']['def'],
                'results': []
            }],
            'senado': [{
                'town_id': town['id'],
                'year': 2023,
                'election_type': "senado",
                'census': data[1]['scope']['censoINE'],
                'participation': data[1]['scope']['escrutinio']['participacion']['def'],
                'abstention': data[1]['scope']['escrutinio']['porcAbstencion']['def'],
                'totalvotes': data[1]['scope']['escrutinio']['votosTotales']['def'],
                'nullvotes': data[1]['scope']['escrutinio']['votosNulos']['def'],
                'emptyvotes': data[1]['scope']['escrutinio']['votosBlancos']['def'],
                'validvotes': data[1]['scope']['escrutinio']['votosValidos']['def'],
                'results': []
            }, {
                'town_id': town['id'],
                'year': 2019,
                'election_type': "senado",
                'census': data[1]['scope']['censoINE'],
                'participation': data[1]['scope']['escrutinioAnt'][0]['participacion']['def'],
                'abstention': data[1]['scope']['escrutinioAnt'][0]['porcAbstencion']['def'],
                'totalvotes': data[1]['scope']['escrutinioAnt'][0]['votosTotales']['def'],
                'nullvotes': data[1]['scope']['escrutinioAnt'][0]['votosNulos']['def'],
                'emptyvotes': data[1]['scope']['escrutinioAnt'][0]['votosBlancos']['def'],
                'validvotes': data[1]['scope']['escrutinioAnt'][0]['votosValidos']['def'],
                'results': []
            }],
        }

        # -- sometimes escrutinioAnt is null --
        census = 0
        participation = 0
        abstention = 0.00
        totalvotes = 0
        nullvotes = 0
        emptyvotes = 0
        validvotes = 0

        # if data['escrutinioAnt'] is not None:
        #    census = data['escrutinioAnt'][0]['censoEscrutado']['def']

        # all_results['elections'].append({
        #    'town_id': town['id'],
        #    'year': 2019,
        #    'election_type': "congreso",
        #    'census': census,
        #    'participation': data['escrutinioAnt'][0]['participacion']['def'],
        #    'abstention': data['escrutinioAnt'][0]['porcAbstencion']['def'],
        #    'totalvotes': data['escrutinioAnt'][0]['votosTotales']['def'],
        #    'nullvotes': data['escrutinioAnt'][0]['votosNulos']['def'],
        #    'emptyvotes': data['escrutinioAnt'][0]['votosBlancos']['def'],
        #    'validvotes': data['escrutinioAnt'][0]['votosValidos']['def']
        # })

        # -- process party results data 2023 --
        # results = []
        # for item in data['escrutinio']['partidos']:
        #     party = {
        #        'town_id': town['id'],
        #        'year': 2023,
        #        'election_type': "generals",
        #        'party': item['siglas'].replace("'", "\\'"),
        #        'votes': item['votos']['def'],
        #        'percentage': item['porcentaje']['def']
        #    }
        #    results.append(party)

        # -- process party results data 2019 --
        # for item in data['escrutinioAnt'][0]['partidos']:
        #    party = {
        #        'town_id': town['id'],
        #        'year': 2019,
        #        'election_type': "locals",
        #        'party': item['siglas'].replace("'", "\\'"),
        #        'votes': item['votos']['def'],
        #        'percentage': item['porcentaje']['def']
        #    }
        #    results.append(party)

        all_results['results'] = results

        # print(all_results)
        # print("-----------------------------------------------")
        # exit()

        return all_results
