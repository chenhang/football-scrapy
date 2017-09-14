from crawlers.spiders.squawka import SquawkaSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from squawka import utils
import json
import subprocess
COMPETITION_IDS = [8, 5, 6, 9, 21, 22, 23, 24]


def load_json(file_name):
    with open(file_name) as json_data:
        d = json.load(json_data)
        return d


def write_json(file_name, json_data):
    with open(file_name, 'w') as outfile:
        json.dump(json_data, outfile)
        return json_data


downloaded = load_json('downloaded.json')
for year in range(2017, 2008, -1):
    for competition_id in COMPETITION_IDS:
        if [competition_id, year] in downloaded:
            print year, utils.COMPETITIONS[competition_id], 'downloaded'
            continue
        print year, utils.COMPETITIONS[competition_id], 'start'
        process = CrawlerProcess(get_project_settings())
        process.crawl(
            SquawkaSpider, competition_id=competition_id, season=year)
        process.start()

        # cmd = [
        #     "scrapy", "crawl squawka -a competition_id=" + str(competition_id)
        #     + " -a season=" + str(year)
        # ]
        # process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        # process.wait()
        # print process.returncode
        print year, utils.COMPETITIONS[competition_id], 'end'
        downloaded.append([competition_id, year])
        write_json('downloaded.json', downloaded)
