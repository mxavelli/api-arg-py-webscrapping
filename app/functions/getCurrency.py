from app.functions.config import country_code_dict
from app.functions.database import insert_database
from bs4 import BeautifulSoup
from datetime import date
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
