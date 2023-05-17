import sqlite3

# get_num_rows(db, table)
# args: db - string, file name of database
#       table - string, name of table
# return: count - integer, numbner of rows in given table
# purpose: get the number of rows of a table
def get_num_rows(table):
    conn = sqlite3.connect("hltv_results.db")
    c = conn.cursor()

    query = 'SELECT COUNT(*) FROM match_history;'
    c.execute(query)
    count = c.fetchone()[0]

    conn.close()
    return count