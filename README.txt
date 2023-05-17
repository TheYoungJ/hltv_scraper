Simple scraper to take match results from HLTV
For now it always adds every match on the site (working on only adding new entries)
Using for future match predicting project

DEPENDENCIES:
    BeautifulSoup
    requests
    sqlite3

#TODO
#only take new entries
#   can create a function to do all and a function to only do new of matches
#       i know how many matches there are when i run this program so i can say new#ofmatches - old#ofmatches = how many i should insert
#   function to do all would be create and function to do new ones can be update