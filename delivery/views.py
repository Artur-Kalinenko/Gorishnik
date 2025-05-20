from django.http import JsonResponse
from .np_api import np_request

def city_autocomplete(request):
    term = request.GET.get("q", "")
    result = np_request("Address", "getCities", {"FindByString": term, "Limit": 10})
    cities = result.get("data", [])
    return JsonResponse([
        {"id": city["Ref"], "text": f"{city['Description']} ({city['AreaDescription']})"}
        for city in cities
    ], safe=False)

def warehouse_autocomplete(request):
    city_ref = request.GET.get("city_ref")
    result = np_request("AddressGeneral", "getWarehouses", {
        "CityRef": city_ref,
        "Limit": 20
    })
    warehouses = result.get("data", [])
    return JsonResponse([
        {"id": wh["Ref"], "text": wh["Description"]}
        for wh in warehouses
    ], safe=False)