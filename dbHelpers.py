import sqlite3

def initDatabase():
    # Connect to SQLite database
    conn = sqlite3.connect('hltv_results.db')
    c = conn.cursor()

    # Create the Players table
    c.execute('DROP TABLE IF EXISTS players')
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY,
            player_name TEXT,
            link TEXT
        )
    ''')

    c.execute('DROP TABLE IF EXISTS teams')
    c.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY,
            team_name TEXT,
            link TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS team_players (
            team_id INTEGER,
            player_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams(team_id),
            FOREIGN KEY (player_id) REFERENCES players(player_id),
            PRIMARY KEY (team_id, player_id)
        )
    ''')

    # Create the PlayerStats table
    c.execute('DROP TABLE IF EXISTS playerStats')
    c.execute('''
        CREATE TABLE playerStats (
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
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

def get_num_rows_matchHistory():
    conn = sqlite3.connect("hltv_results.db")
    c = conn.cursor()

    query = 'SELECT COUNT(*) FROM match_history;'
    c.execute(query)
    count = c.fetchone()[0]

    conn.close()
    return count

def in_table_player(name):
    conn = sqlite3.connect("hltv_results.db")
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM players WHERE player_name = ?', (name,))
    count = c.fetchone()[0]

    if count > 0:
        return True
    else:
        return False
    
def find_playerID_by_name(name):
    conn = sqlite3.connect("hltv_results.db")
    c = conn.cursor()

    c.execute('SELECT player_id FROM players WHERE player_name = ?', (name,))