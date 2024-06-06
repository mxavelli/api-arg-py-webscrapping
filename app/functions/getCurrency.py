from app.functions.config import country_code_dict, headers
from app.functions.database import insert_database
from bs4 import BeautifulSoup
from re import sub
import requests
import json


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

def get_arg_oficial_currency():
    try:
        values = {}
        website = 'https://dolarhoy.com/i/cotizaciones/dolar-oficial'
        request_web = requests.get(website)
        soup = BeautifulSoup(request_web.text, 'html.parser')
        get_p_elements = soup.body.div.find_all('p')
        for p_element in get_p_elements:
            span = p_element.span.extract()
            values[span.get_text()] = float(p_element.get_text())
        return insert_database(values, country_code_dict['ARG_OFICIAL'])
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}


def get_ven_currency():
    try:
        currencys_title_content = []
        currencys_price_content = []
        website = 'https://www.bcv.org.ve/'
        result = requests.get(website, verify=False)
        content = result.text
        soup = BeautifulSoup(content, 'lxml')
        box = soup.find('div', class_='view-tipo-de-cambio-oficial-del-bcv')
        currencys_price = box.findAll('strong')
        currencys_title = box.findAll('span')
        currencys_title = currencys_title[1:len(currencys_title) - 1]
        for n in currencys_title:
            currencys_title_content.append(n.text.strip())
        for j in currencys_price:
            currencys_price_content.append(float(j.text.strip().replace(',', '.')))
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
        website = 'https://www.bcb.gov.br/api/servico/sitebcb/indicadorCambio'
        r = requests.get(website)
        data = dict(r.json())
        compra_venta = data['conteudo'][1]
        values = {
            'Compra': compra_venta['valorCompra'],
            'Venta': compra_venta['valorVenda'],
        }
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
        url = 'https://www.infodolar.com.do/precio-dolar-entidad-banco-popular.aspx'

        values = {}
        x = requests.get(url)
        soup = BeautifulSoup(x.text, 'html.parser')
        column_headers = soup.body.select('table tr:nth-child(1) th:not(:first-of-type, :last-of-type)')
        columns = soup.body.select('table tr:nth-child(2) td:not(:first-of-type, :last-of-type)')
        for index, column in enumerate(columns):
            header = column_headers[index].text
            value = column.get('data-order', column.findAll(text=True, recursive=False))
            values[header] = float(sub("[^\d\.]", "", value))
        return insert_database(values, country_code_dict['DOP_POPU'])
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


def get_pen_currency():
    try:
        url = 'https://www.eleconomista.es/cruce/USDPEN'
        request = requests.get(url, headers=headers)
        soup = BeautifulSoup(request.text, 'html.parser')
        text = soup.body.select('div:has(> .price-row) > span.last-value:nth-child(2)')[0].text  # 3,7521 /$ expected
        text = ''.join(char for char in text if char.isdigit() or char == ',')
        text = text.replace(',', '.')

        values = {
            'Compra': text,
            'Venta': text
        }
        return insert_database(values, country_code_dict['PEN'])
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}

functions_dict = {
    country_code_dict['BRL']: get_brl_currency,
    country_code_dict['VEN']: get_ven_currency,
    country_code_dict['COP']: get_cop_currency,
    country_code_dict['ARG']: get_arg_currency,
    country_code_dict['ARG_OFICIAL']: get_arg_oficial_currency,
    country_code_dict['DOP_POPU']: get_dop_popular_currency,
    country_code_dict['DOP_BANRE']: get_dop_banre_currency,
    country_code_dict['PEN']: get_pen_currency,
}
