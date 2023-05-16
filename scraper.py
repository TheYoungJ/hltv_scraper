import requests
from bs4 import BeautifulSoup
import sqlite3
import math

# Connect to SQLite database
conn = sqlite3.connect('hltv_results.db')
c = conn.cursor()

# Create table to store results
c.execute('''CREATE TABLE IF NOT EXISTS hltv_results
             (id INTEGER PRIMARY KEY, team1 TEXT, team1_score INTEGER, team2 TEXT, team2_score INTEGER, match_type TEXT, winner TEXT, date TEXT, link TEXT)''')

# Scrape HLTV website
offset = 0

url = 'https://www.hltv.org/results?offset=' + str(offset)
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
pages = int(soup.find(class_='pagination-data').text.split()[-1])
pages = math.floor(pages/100)

#TODO
#only take new entries
#   can create a function to do all and a function to only do new of matches
#       i know how many matches there are when i run this program so i can say new#ofmatches - old#ofmatches = how many i should insert
#   function to do all would be create and function to do new ones can be update



# Store teams + scores + winner in database
for i in range(pages):
    url = 'https://www.hltv.org/results?offset=' + str(offset)
    response = requests.get(url)
    offset += 100
    soup = BeautifulSoup(response.content, 'html.parser')
    results = soup.find('div', class_='results-holder allres')
    sublists = results.find_all('div', class_='results-sublist')

    for day in sublists:
        date = day.find(class_='standard-headline').text.replace("Results for ", "").strip()
        matches = day.find_all('div', class_='result-con')

        for match in matches:
            team1 = match.find_all('div', class_='team')[0].text.strip()
            team2 = match.find_all('div', class_='team')[1].text.strip()
            scores = match.find(class_='result-score').text.split(" - ")
            team1Score = int(scores[0])
            team2Score = int(scores[1])
            matchType = match.find('div', class_='map-text').text.strip()
            winner = team1
            if (team2Score > team1Score):
                winner = team2
            link = "hltv.org" + match.find('a').get('href')
            c.execute("INSERT INTO hltv_results (team1, team1_score, team2, team2_score, match_type, winner, date, link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (team1, team1Score, team2, team2Score, matchType, winner, date, link))

# Commit changes and close connection
conn.commit()
conn.close()