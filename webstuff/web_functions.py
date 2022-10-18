import requests


def request_get_data(url, **kwargs):
    result = requests.get(url=url, params=kwargs.get("params")).json()
    return result


