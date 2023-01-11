def convert_dict_to_csv(dict_var):
    try:
        rows = []
        for key in dict_var:
            rows.append("{},{}".format(key, dict_var[key]))
        return "\n".join(rows)
    except Exception as e:
        return {'Status': 'Error', 'Detail': str(e)}
