from flask import Flask
from flask_mysqldb import MySQL
from bs4 import BeautifulSoup
from datetime import date
import os
import requests
import json

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.getenv('DB_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('DB_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASS', 'hola05')
app.config['MYSQL_DB'] = os.getenv('DB_NAME', 'dollar_libre')

mysql = MySQL(app)


def get_arg_currency():
    values = {}
    website = 'https://dolarhoy.com/i/cotizaciones/dolar-blue'
    request_web = requests.get(website)
    soup = BeautifulSoup(request_web.text, 'html.parser')
    get_p_elements = soup.body.div.find_all('p')
    for p_element in get_p_elements:
        span = p_element.span.extract()
        values[span.get_text()] = float(p_element.get_text())
    return values


def insert_database(jsonparam):
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO dollar_libre.dollar (json) VALUES (%s)", [jsonparam])
        mysql.connection.commit()
        return jsonparam
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}


@app.route('/api/v1/argcurrency', methods=['GET'])
def arg_currency():
    jsonCreated = get_arg_currency()
    jsonCreated['date'] = str(date.today())
    jsonInserted = json.dumps(jsonCreated)
    return insert_database(jsonInserted)


@app.route('/api/v1/argcurrency/csv', methods=['GET'])
def arg_currency_csv():
    values = get_arg_currency()
    string = 'compra,{}\n'.format(values['Compra'])
    string += 'venta,{}'.format(values['Venta'])
    return string


if __name__ == '__main__':
    app.run()
