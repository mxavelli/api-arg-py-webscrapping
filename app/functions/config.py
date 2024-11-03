country_code_dict = {
    'ARG': 'ARG',
    'ARG_OFICIAL': 'ARG_OFICIAL',
    'COP': 'COP',
    'BRL': 'BRL',
    'VEN': 'VEN',
    'DOP_POPU': 'DOP_POPU',
    'DOP_BANRE': 'DOP_BANRE',
    'PEN': 'PEN',
    'CLP': 'CLP',
}

return_methods = {
    'json': 'json',
    'csv': 'csv',
}

country_code_label = {
    country_code_dict['ARG'] : 'Argentina',
    country_code_dict['ARG_OFICIAL'] : 'Argentina',
    country_code_dict['COP'] : 'Colombia',
    country_code_dict['BRL'] : 'Brasil',
    country_code_dict['VEN'] : 'Venezuela',
    country_code_dict['DOP_POPU'] : 'República Dominicana Banco Popular',
    country_code_dict['DOP_BANRE'] : 'República Dominicana Banreservas',
    country_code_dict['PEN'] : 'Sol Peruano'
}

headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 '
                          'Safari/537.36',
            'user': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                    'application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept': 'application/json',
            'accept-language': 'en,es-ES;q=0.9,es;q=0.8',
            'pragma': 'no-cache',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1'
        }