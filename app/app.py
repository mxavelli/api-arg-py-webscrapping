from flask import Flask
from bs4 import BeautifulSoup
import requests
import json

app = Flask(__name__)


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
    values = get_arg_currency()
    string = 'compra,{}\n'.format(values['Compra'])
    string += 'venta,{}'.format(values['Venta'])
    return string


if __name__ == '__main__':
    app.run()
