import scraper_locals

from sqlalchemy import create_engine
from sqlalchemy import text


scrap = scrapper.ManageScraper()


def test_open_towns_file():
    scrap.open_towns_file()
    assert len(scrap.tlist) == 6


def test_fill_regions():
    scrap.fill_regions()
    assert scrap.regions[11]['region'] == "Comunitat Valenciana"


def test_get_region():
    result = scrap.get_region("0000000000000000000006b8")
    assert result == "Comunitat Valenciana"


def test_fill_provinces():
    scrap.fill_provinces()
    assert scrap.provinces[1]['province'] == "Alacant/Alicante"


def test_get_province():
    result = scrap.get_province("00000000000000000000014a")
    assert result == "Alacant/Alicante"


def test_towns():
    scrap.get_towns()
    assert scrap.towns_urls[279]['url'] == "https://resultados.locales2023.es/resultados/0/362/90"
