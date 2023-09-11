from datetime import datetime
from datetime import timedelta
import json
import pymysql.cursors
import os


def execute_query(query, params=[], should_return=False):
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASS', 'hola05'),
        database=os.getenv('DB_NAME', 'dollar_currency'),
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    if should_return:
        return cursor.fetchall()
    connection.close()


def insert_database(jsonparam, country_code):

    jsonparam['date'] = str(datetime.utcnow().replace(microsecond=0))
    jsonparam['country_code'] = country_code
    jsonparam['date_dop'] = str(datetime.utcnow().replace(microsecond=0) - timedelta(hours=4))
    jsonparam['date_arg'] = str(datetime.utcnow().replace(microsecond=0) - timedelta(hours=3))
    execute_query(
        "INSERT INTO currency (json, country_code) VALUES (%s, %s)",
        [json.dumps(jsonparam), country_code]
    )
    return jsonparam


def get_currency_from_table(country_code):
    try:
        query = "select json from currency where json_extract(json, '$.country_code') = '{}' order by json_extract(json, '$.date') desc limit 1"\
            .format(country_code)
        results = execute_query(
            query=query,
            should_return=True
        )
        return json.loads(results[0]['json'])
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}

def get_all_currency_from_table():
    try:
        query = "select country_code, json from currency join (select MAX(id) as id from currency group by country_code) cmax on cmax.id = currency.id;"
        results = execute_query(
            query=query,
            should_return=True
        )
        return json.loads(results[0])
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}