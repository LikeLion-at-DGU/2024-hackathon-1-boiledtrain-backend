from django.shortcuts import render
from django.http import JsonResponse
import requests, json, random
from django.conf import settings

BASE_URL = 'http://localhost:8000/'

def search_near_places(request):
    if request.method == "GET":
        # 지하철역 랜덤 추출
        subway_url = f"{BASE_URL}subway/random"
        subway_response = requests.get(subway_url).json()
        if subway_response["SearchSTNBySubwayLineInfo"]:
            place = subway_response["SearchSTNBySubwayLineInfo"]["row"][0]["STATION_NM"]
        else:
            return JsonResponse({'error': 'Station not found'})
        
        # 지하철역의 이름을 추출해서 장소 검색
        rest_api_key = getattr(settings, 'MAP_KEY')
        location_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?fields=formatted_address%2Cname%2Crating%2Copening_hours%2Cgeometry&input={place}&inputtype=textquery&key={rest_api_key}"
        location_response = requests.get(location_url).json()

        # 검색된 정보에서 위도, 경도를 추출하여 근처 장소 검색
        if location_response['candidates']:
            location = location_response['candidates'][0]['geometry']['location']
            lat = location['lat']
            lng = location['lng']
            # 이 부분 수정 가능
            category = 'cafe'
            nearby_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=500&language=kr&type={category}&key={rest_api_key}"
            nearby_response = requests.get(nearby_url).json()
            
            result = {
                'subway_station': location_response['candidates'][0],
                'nearby_places': nearby_response['results']
            }
            return JsonResponse(result)

        else:
            return JsonResponse({'error': 'Place not found'})
    return JsonResponse(location_response)
