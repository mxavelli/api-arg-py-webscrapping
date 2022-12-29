from flask import Flask
from bs4 import BeautifulSoup
import requests
import json
from re import sub

app = Flask(__name__)


def convert_dict_to_csv(dict_var):
    rows = []
    for key in dict_var:
        rows.append("{},{}".format(key, dict_var[key]))
    return "\n".join(rows)


def get_cop_currency():
    values = {}
    website = 'https://www.dolarhoy.co/'
    request_web = requests.get(website)
    soup = BeautifulSoup(request_web.text, 'html.parser')
    h3_element = soup.find('h3', string="Precio en Casas de Cambio")
    row_element = h3_element.find_next_sibling()
    cols_elements = row_element.findChildren('div')
    for child in cols_elements:
        text = child.find('small').get_text()
        value = child.find('span').get_text()
        values[text] = float(sub("[^\d\.]", "", value))
    return values


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


@app.route('/api/v1/argcurrency', methods=['GET'])
def arg_currency():
    return json.dumps(get_arg_currency())


@app.route('/api/v1/argcurrency/csv', methods=['GET'])
def arg_currency_csv():
    return convert_dict_to_csv(get_arg_currency())


@app.route('/api/v1/cop/json', methods=['GET'])
def get_cop_json():
    values = get_cop_currency()
    return json.dumps(values)


@app.route('/api/v1/cop/csv', methods=['GET'])
def get_cop_csv():
    return convert_dict_to_csv(get_cop_currency())


if __name__ == '__main__':
    app.run()
