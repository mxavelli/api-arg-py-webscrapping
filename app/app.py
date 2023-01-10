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
    'DOP_POPU': 'DOP_POPU',
    'DOP_BANRE': 'DOP_BANRE',
}

return_methods = {
    'json': 'json',
    'csv': 'csv',
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

    jsonparam['date'] = str(datetime.utcnow())
    jsonparam['country_code'] = country_code
    execute_query(
        "INSERT INTO currency (json, country_code) VALUES (%s, %s)",
        [json.dumps(jsonparam), country_code]
    )
    return jsonparam


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
        return insert_database(values, country_code_dict['ARG'])
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
        return insert_database(values, country_code_dict['VEN'])
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
        return insert_database(values, country_code_dict['BRL'])
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
        return insert_database(values, country_code_dict['COP'])
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}


def get_dop_popular_currency():
    try:
        url = 'https://popularenlinea.com/_api/web/lists/getbytitle(%27Rates%27)/items?$filter=ItemID%20eq%20%271%27'
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/107.0.0.0 '
                          'Safari/537.36',
            'user': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                    'application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept': 'application/json'
        }

        values = {}
        x = requests.get(url, headers=headers)
        t = json.loads(x.text)
        dic = t['value']

        for d in dic:
            values = d

        data = {
            **values,
            "Compra": values['DollarBuyRate'],
            "Venta": values['DollarSellRate']
        }

        return insert_database(data, country_code_dict['DOP_POPU'])
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}

def get_dop_banre_currency():
    try:
        url = 'https://www.banreservas.com/_layouts/15/SharePointAPI/ObtenerTasas.ashx'
        request = requests.get(url)
        values = json.loads(request.text)
        values = {
            **values,
            **values['info'],
            'Compra': values['compraUS'],
            'Venta': values['ventaUS'],
        }
        del values['info']
        return insert_database(values, country_code_dict['DOP_BANRE'])
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}


functions_dict = {
    country_code_dict['BRL']: get_brl_currency,
    country_code_dict['VEN']: get_ven_currency,
    country_code_dict['COP']: get_cop_currency,
    country_code_dict['ARG']: get_arg_currency,
    country_code_dict['DOP_POPU']: get_dop_popular_currency,
    country_code_dict['DOP_BANRE']: get_dop_banre_currency,
}

@app.route('/', methods=['GET'])
def working():
    return "It's working!"


@app.route('/api/v1/<currency>/<return_method>', methods=['GET'])
def get_currency_as_data(currency, return_method):
    currency = currency.upper()
    if currency not in country_code_dict:
        return json.dumps({
            'error': True,
            'message': 'Currency "{}" not found. Please find available currencies in this json.'.format(currency),
            'data': list(country_code_dict.keys())
        })

    if return_method not in return_methods:
        return json.dumps({
            'error': True,
            'message': 'Return Method "{}" not found. Please find available return methods in this json.'.format(return_method),
            'data': list(return_methods.keys())
        })

    values = get_currency_from_table(country_code_dict[currency])
    if return_methods[return_method] == return_methods['json']:
        return json.dumps(values)
    if return_methods[return_method] == return_methods['csv']:
        return convert_dict_to_csv(values)


@app.route('/api/v1/<currency>/update', methods=['GET'])
def update_currency(currency):
    currency = currency.upper()
    if currency not in country_code_dict:
        return json.dumps({
            'error': True,
            'message': 'Currency "{}" not found. Please find available currencies in this json.'.format(currency),
            'data': list(country_code_dict.keys())
        })

    return functions_dict[currency]()


@app.route('/api/v1/update_all', methods=['GET'])
def update_all_currencies():
    keys = functions_dict.keys()
    values = {}
    for key in keys:
        try:
            result = functions_dict[key]()
            values[key] = result
        except Exception as e:
            values[key] = {
                'error': str(e)
            }

    return json.dumps(values)

if __name__ == '__main__':
    app.run()
