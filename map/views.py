from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.conf import settings


def search_places(request):
    if request.method == "GET":
        # 테스트용
        place = '돌곶이'
        rest_api_key = getattr(settings, 'MAP_KEY')

        location_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={place}&inputtype=textquery&fields=geometry&key={rest_api_key}"
        location_response = requests.get(location_url).json()

        if location_response['candidates']:
            location = location_response['candidates'][0]['geometry']['location']
            lat = location['lat']
            lng = location['lng']
            nearby_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=500&type=restaurant|tourist_attraction&key={rest_api_key}"
            nearby_response = requests.get(nearby_url).json()
            return JsonResponse(nearby_response)
        else:
            return JsonResponse({'error': 'Place not found'})

    return JsonResponse({'error': 'Invalid request'})
