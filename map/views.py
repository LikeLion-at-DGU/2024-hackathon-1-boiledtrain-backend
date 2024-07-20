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
            place = subway_response["SearchSTNBySubwayLineInfo"]["row"][0]["STATION_NM"] + "역"
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

            # place_category.json 파일에서 랜덤 카테고리 추출
            with open('place_category.json', 'r', encoding='utf-8') as f:
                categories = json.load(f)['places']
            # category = random.choice(categories)
            while True:
                category = random.choice(categories)
                nearby_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=500&language=kr&type={category}&key={rest_api_key}"
                nearby_response = requests.get(nearby_url).json()
                if len(nearby_response['results']) != 0 :
                    break 
            
            result = {
                'subway_station': location_response['candidates'][0],
                'category' : category,
                'nearby_places': nearby_response['results']
            }
            return JsonResponse(result)

        else:
            return JsonResponse({'error': 'Place not found'})
    return JsonResponse(location_response)
