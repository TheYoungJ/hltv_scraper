import requests
from bs4 import BeautifulSoup
import sqlite3
import dbHelpers

# populateDatabase()
# args: NONE
# return: NULL
# purpose: Initialize the database and populate it with data scraped from HLTV.org

def initDatabase():
    # Connect to SQLite database
    conn = sqlite3.connect('hltv_results.db')
    c = conn.cursor()

    # Create table to store results
    c.execute('''CREATE TABLE IF NOT EXISTS match_history
                (id INTEGER PRIMARY KEY, team1 TEXT, team1_score INTEGER, team2 TEXT, team2_score INTEGER, match_type TEXT, winner TEXT, date TEXT, link TEXT)''')

    #run update fucntions to populate the db with recent data
    updateMatchHistory()
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    


# updateMatches()
# args: NONE
# return: NULL
# purpose: Update the matches table by only adding matches that are not already in it
def updateMatchHistory():
    # Connect to SQLite database
    conn = sqlite3.connect('hltv_results.db')
    c = conn.cursor()

    offset = 0

    for i in range(1):
        url = 'https://www.hltv.org/results?offset=' + str(offset)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        offset += 100
        numHltv = int(soup.find(class_='pagination-data').text.split()[-1])
        numDb = dbHelpers.get_num_rows('match-history')

        if(numDb >= numHltv or offset >= numHltv):
            break
        
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

    conn.commit()
    conn.close()


def main():
    initDatabase()

main()
