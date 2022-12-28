from flask import Flask
from bs4 import BeautifulSoup
import requests
import json

app = Flask(__name__)

def get_arg_currency():
    kvalues = []
    keys = {'Compra', 'Venta'}
    website = 'https://dolarhoy.com/i/cotizaciones/dolar-blue'
    request_web = requests.get(website)
    soup = BeautifulSoup(request_web.text, 'html.parser')
    getdiv = soup.body.div
    getp = getdiv.find_all('p')
    for i in getp:
        kvalues.append(i.get_text().replace('Compra', '').replace('Venta', ''))
    values = zip(keys, kvalues)
    return dict(values)

@app.route('/api/v1/argcurrency')
def arg_currency():
    return json.dumps(get_arg_currency())

if __name__ == '__main__':
    app.run()
