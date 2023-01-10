from flask import Flask
from flask_cors import CORS
from bs4 import BeautifulSoup
from datetime import datetime, date
from re import sub
import pymysql.cursors
import os
import requests
import json

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

country_code_dict = {
    'ARG': 'ARG',
    'COP': 'COP',
    'BRL': 'BRL',
    'VEN': 'VEN',
}


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
    try:
        jsonparam['date'] = str(datetime.now())
        execute_query(
            "INSERT INTO currency (json, country_code) VALUES (%s, %s)",
            [json.dumps(jsonparam), country_code]
        )
        return jsonparam
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}


def convert_dict_to_csv(dict_var):
    try:
        rows = []
        for key in dict_var:
            rows.append("{},{}".format(key, dict_var[key]))
        return "\n".join(rows)
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}


def get_currency_from_table(country_code):
    try:
        query = "SELECT json FROM currency WHERE country_code='{}' ORDER BY id DESC LIMIT 1".format(country_code)
        results = execute_query(
            query=query,
            should_return=True
        )
        return json.loads(results[0]['json'])
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}


def get_arg_currency():
    try:
        values = {}
        website = 'https://dolarhoy.com/i/cotizaciones/dolar-blue'
        request_web = requests.get(website)
        soup = BeautifulSoup(request_web.text, 'html.parser')
        get_p_elements = soup.body.div.find_all('p')
        for p_element in get_p_elements:
            span = p_element.span.extract()
            values[span.get_text()] = float(p_element.get_text())
        insert_database(values, country_code_dict['ARG'])
        return values
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}


def get_ven_currency():
    try:
        values = {}
        currencys_title_content = []
        currencys_price_content = []
        website = 'https://www.bcv.org.ve/'
        result = requests.get(website, verify=False)
        content = result.text
        soup = BeautifulSoup(content, 'lxml')
        box = soup.find('div', class_='view-tipo-de-cambio-oficial-del-bcv')
        currencys_price = box.findAll('strong')
        currencys_title = box.findAll('span')
        currencys_title = currencys_title[1:len(currencys_title)-1]
        for n in currencys_title:
            currencys_title_content.append(n.text.strip())
        for j in currencys_price:
            currencys_price_content.append(j.text.strip())
        zip_iterator = zip(currencys_title_content, currencys_price_content)
        a_dictionary = dict(zip_iterator)
        values = {
            'Compra': a_dictionary['USD'],
            'Venta': a_dictionary['USD'],
        }
        insert_database(values, country_code_dict['VEN'])
        return values
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}


def get_brl_currency():
    try:
        values = {}
        date_now = date.today()
        website = 'https://www3.bcb.gov.br/bc_moeda/rest/converter/1/1/220/790/{}'.format(date_now)
        request_web = requests.get(website)
        xml_parsed = BeautifulSoup(request_web.text, 'html.parser')
        valor_convertido_element = xml_parsed.findChildren()
        value = valor_convertido_element[0].get_text()
        values['Compra'] = float(value)
        values['Venta'] = float(value)
        insert_database(values, country_code_dict['BRL'])
        return values
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}


def get_cop_currency():
    try:
        values = {}
        website = 'https://www.dolarhoy.co/'
        request_web = requests.get(website)
        soup = BeautifulSoup(request_web.text, 'html.parser')
        h3_element = soup.find('h3', string="Precio en Casas de Cambio")
        row_element = h3_element.find_next_sibling()
        cols_elements = row_element.findChildren('div')
        for child in cols_elements:
            text = child.find('small').get_text().replace('Te venden', 'Venta').replace('Te compran', 'Compra')
            value = child.find('span').get_text()
            values[text] = float(sub("[^\d\.]", "", value))
        insert_database(values, country_code_dict['COP'])
        return values
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}


@app.route('/api/v1/arg/csv', methods=['GET'])
def arg_currency_csv():
    values = get_currency_from_table(country_code_dict['ARG'])
    return convert_dict_to_csv(values)


@app.route('/api/v1/arg/json', methods=['GET'])
def arg_currency_json():
    values = get_currency_from_table(country_code_dict['ARG'])
    return json.dumps(values)


@app.route('/api/v1/arg/update', methods=['GET'])
def arg_currency_update():
    return get_arg_currency()


@app.route('/api/v1/cop/csv', methods=['GET'])
def get_cop_csv():
    values = get_currency_from_table(country_code_dict['COP'])
    return convert_dict_to_csv(values)


@app.route('/api/v1/cop/json', methods=['GET'])
def get_cop_json():
    values = get_currency_from_table(country_code_dict['COP'])
    return json.dumps(values)


@app.route('/api/v1/cop/update', methods=['GET'])
def cop_update():
    return get_cop_currency()


@app.route('/api/v1/brl/csv', methods=['GET'])
def get_brl_csv():
    values = get_currency_from_table((country_code_dict['BRL']))
    return convert_dict_to_csv(values)


@app.route('/api/v1/brl/json', methods=['GET'])
def get_brl_json():
    values = get_currency_from_table(country_code_dict['BRL'])
    return json.dumps(values)


@app.route('/api/v1/brl/update', methods=['GET'])
def brl_update():
    return get_brl_currency()


@app.route('/api/v1/ven/csv', methods=['GET'])
def get_ven_csv():
    values = get_currency_from_table((country_code_dict['VEN']))
    return convert_dict_to_csv(values)


@app.route('/api/v1/ven/json', methods=['GET'])
def get_ven_json():
    values = get_currency_from_table(country_code_dict['VEN'])
    return json.dumps(values)


@app.route('/api/v1/ven/update', methods=['GET'])
def ven_update():
    return get_ven_currency()


@app.route('/', methods=['GET'])
def working():
    return "It's working!!!"


if __name__ == '__main__':
    app.run()
