import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sqlite3
import dbHelpers
import datetime
  
# updateMatches()
# args: NONE
# return: NULL
# purpose: Update the matches table by only adding matches that are not already in it from the past year
def updateMatches():
    # Connect to SQLite database
    conn = sqlite3.connect('hltv_results.db')
    c = conn.cursor()

    offset = 0

    while True:
        date = datetime.datetime.now()
        url = 'https://www.hltv.org/results?offset={}&startDate={}-{:02d}-{:02d}&endDate={}-{:02d}-{:02d}'.format(str(offset), (date.year - 1), date.month, date.day, date.year, date.month, date.day)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        offset += 100
        numHltv = int(soup.find(class_='pagination-data').text.split()[-1])
        numDb = dbHelpers.get_num_rows_matchHistory()
        
        elements = soup.select('.result-con:not(.big-results), .standard-headline:not(.big-results)')

        for element in elements:
            if ('standard-headline' in element['class']):
                date = element.text.split(" for ")[-1]
            elif ('result-con' in element['class'] and date != "Featured results"):
                numDb = dbHelpers.get_num_rows('match-history')
                if (numDb >= numHltv):
                    break
                team1 = element.find_all('div', class_='team')[0].text.strip()
                team2 = element.find_all('div', class_='team')[1].text.strip()
                scores = element.find(class_='result-score').text.split(" - ")
                team1Score = int(scores[0])
                team2Score = int(scores[1])
                matchType = element.find('div', class_='map-text').text.strip()
                winner = team1
                if (team2Score > team1Score):
                    winner = team2
                link = element.find('a').get('href')
                c.execute("INSERT INTO match_history (team1, team1_score, team2, team2_score, match_type, winner, date, link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (team1, team1Score, team2, team2Score, matchType, winner, date, link))

        if(numDb >= numHltv or offset >= numHltv):
            break

    conn.commit()
    conn.close()

# updatePlayers()
# args: NONE
# return: NULL
# purpose: Update the table with all players that have played a game in the past year
def updatePlayers():
    # Connect to SQLite database
    conn = sqlite3.connect('hltv_results.db')
    c = conn.cursor()

    chrome_options = Options().add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)

    date = datetime.datetime.now()
    url = 'https://www.hltv.org/stats/players?startDate={}-{:02d}-{:02d}&endDate={}-{:02d}-{:02d}&minMapCount=0'.format((date.year - 1), date.month, date.day, date.year, date.month, date.day)
    driver.get(url)
    page_source = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page_source, 'html.parser')

    table = soup.find('table', class_='player-ratings-table')
    players = table.find_all('tr')

    for player in players[1:]:
        playerName = player.find(class_='playerCol').find('a').text
        if dbHelpers.in_table_player(playerName):
            break
        playerNationality = player.find('img').get('title')
        playerLink = player.find(class_='playerCol').find('a').get('href').split('?')[0]
        c.execute('INSERT INTO players (player_name, link) VALUES (?,?)', (playerName, playerLink))

    conn.commit()
    conn.close()
        

# updateTeams()
# args: NONE
# return: NULL
# purpose: Update the table with all teams that have played a game in the past year
def updateTeams():
    # Connect to SQLite database
    conn = sqlite3.connect('hltv_results.db')
    c = conn.cursor()

    chrome_options = Options().add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)

    date = datetime.datetime.now()
    url = 'https://www.hltv.org/stats/teams?startDate={}-{:02d}-{:02d}&endDate={}-{:02d}-{:02d}&minMapCount=0'.format((date.year - 1), date.month, date.day, date.year, date.month, date.day)
    driver.get(url)
    page_source = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page_source, 'html.parser')

    table = soup.find('table', class_='player-ratings-table')
    teams = table.find_all('tr')

    for team in teams[1:]:
        teamName = team.find(class_='teamCol-teams-overview').find('a').text
        teamLink = team.find(class_='teamCol-teams-overview').find('a').get('href')
        c.execute('INSERT INTO teams (team_name, link) VALUES (?, ?)', (teamName, teamLink))

        
    conn.commit()
    conn.close()


def main():
    dbHelpers.initDatabase()
    #updateMatches()

    updatePlayers()
    updateTeams()

main()
