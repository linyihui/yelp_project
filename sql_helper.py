import MySQLdb
import json
import pandas as pd
import sys

CREATE_TABLE_STR = ''' (
      categories VARCHAR(1024) CHARACTER SET utf8,
      display_phone VARCHAR(32) CHARACTER SET utf8,
      id VARCHAR(128) CHARACTER SET utf8,
      location VARCHAR(1024) CHARACTER SET utf8,
      menu_date_updated INT,
      menu_provider VARCHAR(128) CHARACTER SET utf8,
      mobile_url VARCHAR(1024) CHARACTER SET utf8,
      name VARCHAR(1024) CHARACTER SET utf8,
      phone VARCHAR(32),
      rating NUMERIC(2, 1),
      rating_img_url VARCHAR(1024) CHARACTER SET utf8,
      rating_img_url_large VARCHAR(1024) CHARACTER SET utf8,
      rating_img_url_small VARCHAR(1024) CHARACTER SET utf8,
      review_count INT,
      snippet_image_url VARCHAR(1024) CHARACTER SET utf8,
      snippet_text VARCHAR(1024) CHARACTER SET utf8,
      url VARCHAR(1024) CHARACTER SET utf8
  );
  '''

COL_LIST = [
  'categories', 
  'display_phone', 
  'id', 
  'location',
  'menu_date_updated',
  'menu_provider',
  'mobile_url',
  'name',
  'phone',
  'rating',
  'rating_img_url',
  'rating_img_url_large',
  'rating_img_url_small',
  'review_count',
  'snippet_image_url',
  'snippet_text',
  'url',
  ]


def readJsonFile(filename):
  with open(filename, 'r') as f:
    return json.load(f)

def initSqlConnection(host, user, passwd, db):
  conn = MySQLdb.connect(host, user, passwd, db)
  with conn:    
    conn.set_character_set('utf8')
    cur = conn.cursor()
    cur.execute('SET NAMES utf8;')
    cur.execute('SET CHARACTER SET utf8;')
    cur.execute('SET character_set_connection=utf8;')
    cur.execute('SET character_set_connection=utf8;')
  return conn

def createSqlTable(conn, table):
  with conn:
    cur = conn.cursor()
    try:
      cur.execute("CREATE TABLE IF NOT EXISTS " + table + CREATE_TABLE_STR)
    except Exception as e:
      print "Exception: ", str(e)
  
def insertBusinessToSqlTable(conn, table, business):
  with conn:
    cur = conn.cursor()
    insert_command = "INSERT INTO %s(" % table;
    keys_in_col_list = [k for k in business.keys() if k in COL_LIST]
    insert_command += ", ".join(keys_in_col_list)
    insert_command += ") VALUES ("

    value_list = []
    for k, v in business.items():
      if k in COL_LIST:
        if isinstance(v, (list, dict, basestring)):
          formatted_str = unicode(v).replace("'", "''")
          value_list.append("'%s'" % formatted_str)
        else:
          value_list.append(str(v))
    insert_command += ", ".join(value_list)
    insert_command += ");"

    try:
      cur.execute(insert_command)
    except Exception as e:
      print "Exception at cur.execute(insert_command): ", str(e)
      # print insert_command

def sqlTableToDataFrame(conn, table, limit=None):
  with conn:
    cur = conn.cursor()
    if not limit:
      cur.execute("SELECT * FROM %s" % table)
    else:
      cur.execute("SELECT * FROM %s LIMIT %d" % (table, limit))
    rows = cur.fetchall()
    df = pd.DataFrame([row for row in rows], columns=[i[0] for i in cur.description])
    return df
