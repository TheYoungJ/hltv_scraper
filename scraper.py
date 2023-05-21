import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sqlite3
import dbHelpers
import datetime

# populateDatabase()
# args: NONE
# return: NULL
# purpose: Initialize the database and populate it with data scraped from HLTV.org

def initDatabase():
    # Connect to SQLite database
    conn = sqlite3.connect('hltv_results.db')
    c = conn.cursor()

    # Create the Players table
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY,
            player_name TEXT,
            date_of_birth TEXT,
            nationality TEXT,
            team_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES Teams(team_id)
        )
    ''')

    # Create the PlayerStats table
    c.execute('''
        CREATE TABLE PlayerStats (
            stat_id INTEGER PRIMARY KEY,
            player_id INTEGER,
            kills INTEGER,
            deaths INTEGER,
            headshot_percentage REAL,
            damage_per_round REAL,
            FOREIGN KEY (player_id) REFERENCES Players(player_id)
        )
    ''')

    # Create table to store results
    c.execute('''
        CREATE TABLE IF NOT EXISTS match_history
            (id INTEGER PRIMARY KEY,
            team1 TEXT,
            team1_score INTEGER,
            team2 TEXT,
            team2_score INTEGER,
            match_type TEXT,
            winner TEXT,
            date TEXT,
            link TEXT
        )
    ''')

    #run update fucntions to populate the db with recent data
    updateMatches()
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    


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
        numDb = dbHelpers.get_num_rows('match-history')
        
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
                link = "hltv.org" + element.find('a').get('href')
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
        playerTeam = player.find(class_='teamCol').get('data-sort')
        playerNationality = player.find('img').get('title')
        print("player: " + playerName + " " + playerTeam + " " + playerNationality)
        break

# updateTeams()
# args: NONE
# return: NULL
# purpose: Update the table with all players that have played a game in the past year


def main():
    #initDatabase()
    #updateMatches()

    updatePlayers()

main()
