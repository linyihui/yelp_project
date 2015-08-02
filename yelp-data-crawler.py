import csv
import json
import re
import time
import sql_helper
from yelpapi import YelpAPI

NUM_TOP_CITIES = 100
MAX_NUM_RESULTS = 1000
OUTPUT_SQL_TABLE = 'yelp_db_us_top_100'

# OAuth credential placeholders that must be filled in by users.
CONSUMER_KEY = "mQj3x5Dgf5YlhQ-XwOkdRg"
CONSUMER_SECRET = "FuGvfcZaDoaQuoQ6y73qFxcjhl4"
TOKEN = "18r5sbfCOqLvnBLJuoEzwczri7f6dadP"
TOKEN_SECRET = "qvCId-RPkUNYu3RVoKPBk5WHovI"

def main():
  cities = []
  with open('top_us_cities.csv', 'r') as f:
    rows = csv.reader(f)
    for r in rows:
       cities.append(r[1] + ', ' + r[2])
  print cities
  
  # Initialize connection with SQL server.
  conn = sql_helper.initSqlConnection('localhost', 'yihui', '', 'db');
  # Create a new table in SQL database if not exists.
  sql_helper.createSqlTable(conn, OUTPUT_SQL_TABLE)

  # Establish connection with Yelp API.
  yelp_api = YelpAPI(CONSUMER_KEY, CONSUMER_SECRET, TOKEN, TOKEN_SECRET)  

  for city_id, city in enumerate(cities[:NUM_TOP_CITIES]):
    print "Processing city #%d: %s" % (city_id, city)
    offset = 0
    businesses = []
    while True:
      # print "offset =", offset
      try:
        search_results = yelp_api.search_query(term='Restaurants', location=city, offset=offset)
        time.sleep(0.1)
      except Exception as e:
        print "Exception: ", str(e)
        break
      offset = offset + 20
      if not search_results['businesses'] or offset > MAX_NUM_RESULTS:
        print "not search_results['businesses'] or offset > MAX_NUM_RESULTS."
        break
      else:
        businesses.extend(search_results['businesses'])
        for business in search_results['businesses']:
          sql_helper.insertBusinessToSqlTable(conn, OUTPUT_SQL_TABLE, business)
    print "Number of results offset=", offset

    # Write to JSON file.
    city_filestr = city
    city_filestr = re.sub(r",\s", '_', city_filestr)
    city_filestr = re.sub(r"\s+", '-', city_filestr)
    print city_filestr
    try:
      with open('Restaurants_'+ city_filestr + '.json', 'w') as f:
        json.dump(businesses, f)
    except:
      print "Error writing JSON file."

if __name__ == "__main__":
  main()