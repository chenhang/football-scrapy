# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import os
import time
import json

TOURMENTS = [
    "Bundesliga", "UEFA Europa League", "Premier League", "Serie A", "La Liga",
    "Ligue 1", "Eredivisie", "Liga NOS", "UEFA Champions League"
]
SKIP = False
NO_HISTORY_PAGES = [
    'https://www.whoscored.com/Teams/779/Show/Italy-Crotone',
    'https://www.whoscored.com/Teams/60/Show/Spain-Alaves',
    'https://www.whoscored.com/Teams/825/Show/Spain-Leganes',
    'https://www.whoscored.com/Teams/8071/Show/Portugal-Tondela',
    'https://www.whoscored.com/Teams/108/Show/Portugal-Moreirense',
    'https://www.whoscored.com/Teams/5948/Show/Portugal-Arouca',
    'https://www.whoscored.com/Teams/122/Show/Portugal-Boavista',
    'https://www.whoscored.com/Teams/2187/Show/Portugal-Feirense',
    'https://www.whoscored.com/Teams/298/Show/Portugal-Vitoria-de-Setubal',
    'https://www.whoscored.com/Teams/2008/Show/Portugal-Chaves',
    'https://www.whoscored.com/Teams/936/Show/Portugal-Nacional',
    'https://www.whoscored.com/Teams/303/Show/Netherlands-Sparta-Rotterdam',
]


def load_json(file_name):
    with open(file_name) as json_data:
        d = json.load(json_data)
        return d


def write_json(file_name, json_data):
    with open(file_name, 'w') as outfile:
        json.dump(json_data, outfile)
        return json_data


def get_error_teams(driver, file_name):
    errors = load_json(file_name)
    print(len(errors.keys()))
    for team_id in errors.keys():
        info = errors[team_id]
        league = info['league'].split('/')[-1]
        team_name = '-'.join(info['name'].split('/')[-1].split('-')[0:-1])
        url = "https://www.whoscored.com/Teams/" + team_id + "/Show/" + team_name

        start_time = time.time()
        get_team_index(driver, league, url)
        print("Team cost: --- %s seconds ---" % (time.time() - start_time))

        del errors[team_id]
        errors = write_json(file_name, errors)
        print(len(errors.keys()))


def get_leagues(driver, league_urls):
    for url in league_urls:
        print(url)
        start_time = time.time()
        get_league_teams(driver, url)
        print("League cost: --- %s seconds ---" % (time.time() - start_time))


def get_league_teams(driver, url):
    global SKIP
    team_links = get_league_team_urls(driver, url)
    if len(url.split('/')) <= 8:
        league_key = url.split('/')[-1] + '-' + url.split('/')[-2]
    else:
        league_key = '-'.join(
            url.split('/')[-1].split('-')[:-2]) + '-' + url.split(
                '/')[url.split('/').index('Tournaments') + 1]
    for key, url in team_links.iteritems():
        if url == 'https://www.whoscored.com/Teams/69/Show/Spain-Malaga':
            SKIP = False
        if not SKIP:
            start_time = time.time()
            get_team_index(driver, league_key, url)
            print("Team cost: --- %s seconds ---" % (time.time() - start_time))


def get_league_team_urls(driver, url):
    driver.get(url)
    html = driver.page_source
    team_links = {}
    for element in driver.find_elements_by_class_name('team-link'):
        link = element.get_attribute('href')
        splited_link = link.split('/')
        if not team_links.has_key(splited_link[-3]) and len(
                splited_link
        ) == 7 and len(splited_link[-1].split(
                '-')[0]) > 0 and not splited_link[-1].split('-')[0].isdigit():
            # if len(splited_link) == 7 and len(splited_link[-1].split('-')[0]) > 0:
            team_links[splited_link[-3]] = link
    return team_links


def get_all_fixtures(driver, team_key, url):
    fixture_url = url.replace('/Show/', '/Fixtures/')
    driver.get(fixture_url)
    time.sleep(3)
    path = root_path_for(team_key + '/Overall')
    with open(path + 'Fixtures.html', 'w') as file:
        file.write(driver.page_source)


def get_all_stats(driver, team_key, url):
    stats_url = url.replace('/Show/', '/Statistics/')
    driver.get(stats_url)
    time.sleep(4)
    path = root_path_for(team_key + '/Overall')
    with open(path + 'Statistics.html', 'w') as file:
        file.write(driver.page_source)

    for i, element in enumerate(
            driver.find_elements_by_xpath(
                '//*[@id="team-situation-stats-options"]/li/a')):
        ajax_click(driver, element)
        time.sleep(4)
        if i != 2:
            for option in driver.find_elements_by_xpath(
                    '//*[@id="' + element.get_attribute("href").split('#')[-1]
                    + '-filter-against"]/dl/dd'):
                file_name = '_'.join([element.text, option.text]) + '.html'
                ajax_click(driver, option)
                time.sleep(4)
                with open(path + file_name, 'w') as file:
                    file.write(driver.page_source)
        else:
            file_name = element.text + '.html'
            with open(path + file_name, 'w') as file:
                file.write(driver.page_source)

    for i, element in enumerate(
            driver.find_elements_by_xpath(
                '//*[@id="team-pitch-stats-options"]/li')):
        ajax_click(driver, element)
        time.sleep(4)
        if i == 1:
            for option in driver.find_elements_by_xpath(
                    '//*[@id="team-attempts-filter-against"]/dl/dd'):
                ajax_click(driver, option)
                time.sleep(4)
                file_name = '_'.join([element.text, option.text]) + '.html'
                with open(path + file_name, 'w') as file:
                    file.write(driver.page_source)
        else:
            file_name = element.text + '.html'
            with open(path + file_name, 'w') as file:
                file.write(driver.page_source)


def get_history(driver, team_key, url):
    history_url = url.replace('/Show/', '/Archive/')
    history_paths = load_json('history_paths.json')
    team_id = team_key.split('-')[-1]
    if url in NO_HISTORY_PAGES or team_id not in ['26', '53', '276']:
        return
    driver.get(history_url)
    time.sleep(5)
    path = root_path_for(team_key)
    print path
    options = driver.find_element_by_xpath(
        '//*[@id="stageId"]').find_elements_by_tag_name('option')
    option_length = len(options)
    infos = map(lambda option: option.text.split(' - '), options)
    print option_length
    for i in range(0, option_length):
        info = infos[i]
        name = info[0]
        season = season_dir(info[1])
        key = "_".join([team_key, name, season])
        downloaded = False
        print "Getting: " + "_".join(info)
        for dl_key in history_paths.keys():
            if dl_key.split('_')[-1] == season and dl_key.split('_')[-3].split(
                    '-')[-1] == team_id and dl_key.split('_')[-2] == name:
                downloaded = True
                break
        if name not in TOURMENTS or downloaded:
            print "Skip: " + "_".join(info)
            continue
        options = driver.find_element_by_xpath(
            '//*[@id="stageId"]').find_elements_by_tag_name('option')
        option = options[i]
        ajax_click(driver, option)
        time.sleep(2)

        path = root_path_for(team_key + '/' + name + '/' + season)
        with open(path + 'Summary.html', 'w') as file:
            file.write(driver.page_source)

        for element in driver.find_elements_by_class_name(
                'in-squad-detailed-view'):
            file_name = element.text + '.html'
            ajax_click(driver, element)
            time.sleep(2)
            with open(path + file_name, 'w') as file:
                file.write(driver.page_source)

        detailed_path = root_path_for(team_key + '/' + name + '/' + season +
                                      '/players')
        category_selection = driver.find_element_by_xpath(
            '//*[@id="category"]')
        category_options = category_selection.find_elements_by_tag_name(
            'option')
        for category_option in category_options:
            ajax_click(driver, category_option)
            sub_category_selection = driver.find_element_by_xpath(
                '//*[@id="subcategory"]')
            sub_category_options = sub_category_selection.find_elements_by_tag_name(
                'option')
            for sub_category_option in sub_category_options:
                ajax_click(driver, sub_category_option)
                accumulation_type_selection = driver.find_element_by_xpath(
                    '//*[@id="statsAccumulationType"]')
                accumulation_type_options = accumulation_type_selection.find_elements_by_tag_name(
                    'option')
                for accumulation_type_option in accumulation_type_options:
                    ajax_click(driver, accumulation_type_option)
                    file_name = '-'.join([
                        category_option.text, sub_category_option.text,
                        accumulation_type_option.text
                    ]) + '.html'
                    with open(detailed_path + file_name, 'w') as file:
                        file.write(driver.page_source)
        view_length = len(
            driver.find_element_by_xpath(
                '//*[@id="team-formations-filter-type"]/dl')
            .find_elements_by_class_name('option'))
        for i in range(0, view_length):
            view_options = driver.find_element_by_xpath(
                '//*[@id="team-formations-filter-type"]/dl'
            ).find_elements_by_class_name('option')
            view_option = view_options[i]
            view_name = view_option.text
            ajax_click(driver, view_option)
            path = root_path_for(team_key + '/' + name + '/' + season + '/' +
                                 view_name + '/')
            if i != 1:
                with open(path + 'Formation.html', 'w') as file:
                    file.write(driver.page_source)
            else:
                formation_length = len(
                    driver.find_element_by_xpath(
                        '//*[@id="team-formations-filter-formation"]/dl')
                    .find_elements_by_class_name('option'))
                for k in range(0, formation_length):
                    formation_options = driver.find_element_by_xpath(
                        '//*[@id="team-formations-filter-formation"]/dl'
                    ).find_elements_by_class_name('option')
                    formation_option = formation_options[k]
                    formation_name = formation_option.text
                    if not formation_name:
                        driver.execute_script("$('a#formation-filter')[" +
                                              str(k) + "].click()")
                        formation_name = driver.execute_script(
                            "return $('a#formation-filter')[" + str(k) +
                            "].text")
                    else:
                        ajax_click(driver, formation_option)
                    with open(path + formation_name + '.html', 'w') as file:
                        file.write(driver.page_source)
        history_paths[key] = True
        print 'Done, continue to next'
        write_json('history_paths.json', history_paths)


def get_all_formations(driver, team_key):
    view_length = len(
        driver.find_element_by_xpath(
            '//*[@id="team-formations-filter-type"]/dl')
        .find_elements_by_class_name('option'))
    for i in range(0, view_length):
        view_options = driver.find_element_by_xpath(
            '//*[@id="team-formations-filter-type"]/dl'
        ).find_elements_by_class_name('option')
        view_option = view_options[i]
        name = view_option.text
        ajax_click(driver, view_option)
        tournament_length = len(
            driver.find_element_by_xpath(
                '//*[@id="team-formations-filter-stageId"]/dl')
            .find_elements_by_class_name('option'))
        for j in range(0, tournament_length):
            tournament_options = driver.find_element_by_xpath(
                '//*[@id="team-formations-filter-stageId"]/dl'
            ).find_elements_by_class_name('option')
            tournament_option = tournament_options[j]
            tournament_name = tournament_option.text
            ajax_click(driver, tournament_option)
            time.sleep(3)
            path = root_path_for(team_key + '/' + tournament_name + '/' +
                                 '2017-2018/' + name)
            if i != 0:
                with open(path + 'Formation.html', 'w') as file:
                    file.write(driver.page_source)
            else:
                formation_length = len(
                    driver.find_element_by_xpath(
                        '//*[@id="team-formations-filter-formation"]/dl')
                    .find_elements_by_class_name('option'))
                for k in range(0, formation_length):
                    formation_options = driver.find_element_by_xpath(
                        '//*[@id="team-formations-filter-formation"]/dl'
                    ).find_elements_by_class_name('option')
                    formation_option = formation_options[k]
                    formation_name = formation_option.text
                    if not formation_name:
                        driver.execute_script("$('a#formation-filter')[" +
                                              str(k) + "].click()")
                        formation_name = driver.execute_script(
                            "return $('a#formation-filter')[" + str(k) +
                            "].text")
                    else:
                        ajax_click(driver, formation_option)
                    with open(path + formation_name + '.html', 'w') as file:
                        file.write(driver.page_source)
        ajax_click(driver,
                   driver.find_element_by_xpath(
                       '//*[@id="team-formations-filter-stageId"]/dl/dd[1]/a'))


def get_all_players(driver, team_key):
    tournament_length = len(
        driver.find_element_by_xpath('//*[@id="tournamentOptions"]')
        .find_elements_by_class_name('option'))
    for i in range(0, tournament_length):
        tournament_options = driver.find_element_by_xpath(
            '//*[@id="tournamentOptions"]').find_elements_by_class_name(
                'option')
        tournament_option = tournament_options[i]
        name = tournament_option.text

        ajax_click(driver, tournament_option)
        time.sleep(3)
        path = root_path_for(team_key + '/' + name + '/2017-2018')
        with open(path + 'Summary.html', 'w') as file:
            file.write(driver.page_source)

        for element in driver.find_elements_by_class_name(
                'in-squad-detailed-view'):
            file_name = element.text + '.html'
            ajax_click(driver, element)
            time.sleep(3)
            with open(path + file_name, 'w') as file:
                file.write(driver.page_source)

        detailed_path = root_path_for(team_key + '/' + name + '/2017-2018' +
                                      '/players')
        category_selection = driver.find_element_by_xpath(
            '//*[@id="category"]')
        category_options = category_selection.find_elements_by_tag_name(
            'option')
        for category_option in category_options:
            ajax_click(driver, category_option)
            sub_category_selection = driver.find_element_by_xpath(
                '//*[@id="subcategory"]')
            sub_category_options = sub_category_selection.find_elements_by_tag_name(
                'option')
            for sub_category_option in sub_category_options:
                ajax_click(driver, sub_category_option)
                accumulation_type_selection = driver.find_element_by_xpath(
                    '//*[@id="statsAccumulationType"]')
                accumulation_type_options = accumulation_type_selection.find_elements_by_tag_name(
                    'option')
                for accumulation_type_option in accumulation_type_options:
                    ajax_click(driver, accumulation_type_option)
                    name = '-'.join([
                        category_option.text, sub_category_option.text,
                        accumulation_type_option.text
                    ]) + '.html'
                    with open(detailed_path + name, 'w') as file:
                        file.write(driver.page_source)

        ajax_click(driver,
                   driver.find_element_by_xpath(
                       '//*[@id="team-squad-stats-options"]/li[1]/a'))


def get_team_index(driver, league_key, url):
    # driver.get(url)
    # while True:
    #     try:
    #         WebDriverWait(driver, 100).until(
    #             ajax_complete, "Timeout waiting for page to load")
    #     except WebDriverException:
    #         print "Timeout, retrying..."
    #         continue
    #     else:
    #         break
    team_key = league_key + '/' + url.split('/')[-1] + '-' + url.split('/')[-3]
    print(url)
    # get_all_players(driver, team_key)
    # get_all_formations(driver, team_key)
    get_all_fixtures(driver, team_key, url)
    get_all_stats(driver, team_key, url)
    # get_history(driver, team_key, url)


def root_path_for(team):
    path = 'teams/' + team + '/'
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def element_visiable(driver, class_name):
    len([
        e for e in driver.find_elements_by_class_name(class_name)
        if e.value_of_css_property('display') != 'none'
    ]) > 0


def ajax_complete(driver):
    try:
        return 0 == driver.execute_script(
            "return jQuery.active"
        )  # and ((not element_visiable(driver, 'loading-wrapper')) or element_visiable(driver, 'statistics-table-tab'))
    except WebDriverException:
        pass


def ajax_click(driver, element):
    element.click()
    WebDriverWait(driver, 10000).until(ajax_complete,
                                       "Timeout waiting for page to load")
    time.sleep(1)


def season_dir(season):
    return '-'.join(season.split('/'))


BASE_URL = "https://www.whoscored.com"
pl_url = "https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League"
ia_url = "https://www.whoscored.com/Regions/108/Tournaments/5/Italy-Serie-A"
league_urls = [
    "https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League",
    "https://www.whoscored.com/Regions/81/Tournaments/3/Germany-Bundesliga",
    "https://www.whoscored.com/Regions/108/Tournaments/5/Italy-Serie-A",
    "https://www.whoscored.com/Regions/206/Tournaments/4/Spain-La-Liga",
    "https://www.whoscored.com/Regions/74/Tournaments/22/France-Ligue-1",
    "https://www.whoscored.com/Regions/177/Tournaments/21/Portugal-Liga-NOS",
    "https://www.whoscored.com/Regions/155/Tournaments/13/Seasons/6826/Netherlands-Eredivisie",
]
driver = webdriver.Chrome()
driver.implicitly_wait(1000)
# get_error_teams(driver, 'parse_teams_stats_error.json')
# get_team_index(driver, 'England-Premier-League-2/', "https://www.whoscored.com/Teams/32/Show/England-Manchester-United")
# get_team_index(
#     driver, 'test',
#     "https://www.whoscored.com/Teams/32/Show/England-Manchester-United")
# print get_league_team_urls(
#     driver,
#     "https://www.whoscored.com/Regions/108/Tournaments/5/Italy-Serie-A")
# get_all_stats(driver, 'Spain-Barcelona-65',
#               'https://www.whoscored.com/Teams/63/Show/Spain-Atletico-Madrid')
get_leagues(driver, league_urls)
driver.quit()
