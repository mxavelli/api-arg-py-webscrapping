from flask import Flask, jsonify
from flask_cors import CORS
from app.functions.config import country_code_dict, return_methods, country_code_label
from app.functions.convertToCsv import convert_dict_to_csv
from app.functions.database import get_currency_from_table, get_all_currency_from_table
from app.functions.getCurrency import functions_dict
from app.functions.createGraphic import create_loan_graphic
import json

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/', methods=['GET'])
def working():
    return "It's working!"


@app.route('/api/v1/<currency>/<return_method>', methods=['GET'])
def get_currency_as_data(currency, return_method):
    currency = currency.upper()
    if currency == 'ALL':
        values = get_all_currency_from_table()
        return json.dumps(values)
    if currency not in country_code_dict:
        return json.dumps({
            'error': True,
            'message': 'Currency "{}" not found. Please find available currencies in this json.'.format(currency),
            'data': list(country_code_dict.keys())
        })

    if return_method not in return_methods:
        return json.dumps({
            'error': True,
            'message': 'Return Method "{}" not found. Please find available return methods in this json.'
            .format(return_method),
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

@app.route('/api/v1/get_currencies_label', methods=['GET'])
def get_currencies_label():
    return jsonify(country_code_label)


@app.route('/api/v1/graphic/<amount>/<monthly_interest_rate>', methods=['GET'])
def get_graphic(amount, monthly_interest_rate):
    base64 = create_loan_graphic(float(amount), float(monthly_interest_rate) / 100)
    return json.dumps({
        'image_png': base64,
        'amount': amount,
        'monthly_interest_rate': monthly_interest_rate,
        'converted_monthly_interest_rate': float(monthly_interest_rate) / 100,
        'image_png_src': 'data:image/png;base64, ' + base64
    })

if __name__ == '__main__':
    app.run()
