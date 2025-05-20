import requests
from django.conf import settings

API_URL = "https://api.novaposhta.ua/v2.0/json/"

def np_request(model_name, called_method, method_properties):
    data = {
        "apiKey": settings.NOVA_POSHTA_API_KEY,
        "modelName": model_name,
        "calledMethod": called_method,
        "methodProperties": method_properties
    }
    response = requests.post(API_URL, json=data)
    return response.json()
