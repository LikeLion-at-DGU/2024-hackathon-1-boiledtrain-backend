from django.shortcuts import render
from django.http import JsonResponse
import requests, json, random, os
from django.conf import settings
from rest_framework import viewsets, mixins
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import time


BASE_URL = 'http://localhost:8000/'

excluded_keywords = [
            'Dunkin', '배스킨라빈스', 'KFC', 'Outback Steakhouse', "Domino's", 'Bonjuk', 'Burger King',
            '네네치킨', 'Pelicana Chicken', 'Bonjug', 'Pizza Maru', '파리바게', 'Paris Baguette', '뚜레쥬르', 'Tous Les Jours',
            'Starbucks', '스타벅스', 'LOTTERIA', '설빙', 'Sulbing', 'Hollys', "Holly's", '인쌩맥주', '장미맨숀', 'Ediya', 
            'Pizza School', 'Daiso', 'KyoChon', 'Kyochon', "Mom's Touch", '스터디카페', '키즈카페', '7080', '상가', 
            '프라자', 'plaza', 'Pizza Hut', 'Compose Coffee', 'Mega Coffee', 'Krispy Kreme', '로봇카페', '무인카페', 
            '커스텀커피', 'Chicken Mania', 'BHC', 'BBQ', 'The Coffee Bean', '교촌', '피씨카페', 'Twosome Place', '샵', 
            '메가커피', '메가엠지씨커피', 'Fitness', '멕시카나', 'Tom N Toms', 'Puradak Chicken', 'COFFEE BAY', '페리카나', 
            'paris baguette', 'Pascucci', 'Gongcha', "Paik's"
        ]

###################################################
# 랜덤 여행
def search_places_random(request):
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
        location_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?fields=formatted_address%2Cname%2Crating%2Copening_hours%2Cgeometry&input={place}&inputtype=textquery&key={rest_api_key}&language=ko"
        location_response = requests.get(location_url).json()

        # 검색된 정보에서 위도, 경도를 추출하여 근처 장소 검색
        if location_response['candidates']:
            location = location_response['candidates'][0]['geometry']['location']
            lat = location['lat']
            lng = location['lng']

            # place_category.json 파일에서 랜덤 카테고리 추출
            with open('place_category.json', 'r', encoding='utf-8') as f:
                categories = json.load(f)['places']

            # 지하철 정보 json 저장
            selected_places_ids = set()  # 중복 체크를 위한 장소 ID 집합
            selected_categories = set()  # 중복 체크를 위한 카테고리 집합
            test = []
            for _ in range(3):  # 3번 반복
                while True:
                    available_categories = [category for category in categories if category not in selected_categories]
                    if not available_categories:
                        break
                    category = random.choice(available_categories)

                    # 시간 조건
                    if category == "bar":
                        current_hour = datetime.now().hour
                        if not (15 <= current_hour <= 22):  # 오후 3시 ~ 오후 10시 사이가 아닐 경우
                            continue

                    nearby_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=1000&language=ko&type={category}&key={rest_api_key}&language=ko"
                    nearby_response = requests.get(nearby_url).json()

                    # rating이 4.0 이상인 곳만 필터링
                    filtered_places = [place for place in nearby_response['results']
                                        if place.get('rating', 0) >= 4.0
                                        and not place.get('name', '').endswith(('점', '역', 'station)', '점)'))
                                        and not any(keyword in place.get('name', '') for keyword in excluded_keywords)
                                        and place.get('user_ratings_total', 0) >= 5
                                        and place.get('place_id') not in selected_places_ids  # 중복 체크
                                        ]
                    if len(filtered_places) != 0:
                        break

                # 필터링된 장소에서 랜덤으로 하나 선택
                selected_place = random.choice(filtered_places)
                selected_places_ids.add(selected_place['place_id'])  # 선택된 장소 ID 저장
                selected_categories.add(category)  # 선택된 카테고리 저장

                test.append({
                    'category': category,
                    'nearby_place': {
                        'name' : selected_place['name'],
                        'rating' : selected_place['rating'],
                        'user_ratings_total' : selected_place['user_ratings_total']
                    }
                })

            results = {'subway_station': location_response['candidates'][0]['name'], 'test' : test}
            result = {
                'results': results  # 3개의 카테고리와 장소를 포함
            }
            return JsonResponse(result)

        else:
            return JsonResponse({'error': 'Place not found'})
    return JsonResponse(location_response)
###################################################################
# 목적 여행
def search_places_category(request):
    if request.method == "GET":
        user_category = 'amusement_park'
        result = []
        i = 0 # 인덱스

        # selected_stations = set()  # 중복 체크를 위한 지하철역 집합
        with open('station_nm_list.json', 'r', encoding='utf-8') as file:
            station_nm_list = json.load(file)
        random.shuffle(station_nm_list)
        for _ in range(3):  # 3번 반복
            while True:  # 조건에 맞는 장소가 나올 때까지 반복
                # 지하철역 랜덤 추출
                cur_time = time.time()
                # subway_url = f"{BASE_URL}subway/random"
                # subway_response = requests.get(subway_url).json()
                # if subway_response["SearchSTNBySubwayLineInfo"]:
                #     station_name = subway_response["SearchSTNBySubwayLineInfo"]["row"][0]["STATION_NM"]
                #     if station_name in selected_stations:
                #         continue
                    
                #     selected_stations.add(station_name)
                #     place = station_name + "역" 
                # else:
                #     return JsonResponse({'error': 'Station not found'})
                

                place = station_nm_list[i] + "역"
                i = i + 1
                # 지하철역의 이름을 추출해서 장소 검색
                rest_api_key = settings.MAP_KEY
                location_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?fields=formatted_address%2Cname%2Crating%2Copening_hours%2Cgeometry&input={place}&inputtype=textquery&key={rest_api_key}&language=ko"
                location_response = requests.get(location_url).json()

                # 검색된 정보에서 위도, 경도를 추출하여 근처 장소 검색
                if location_response['candidates']:
                    location = location_response['candidates'][0]['geometry']['location']
                    lat = location['lat']
                    lng = location['lng']

                    nearby_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=1000&language=ko&type={user_category}&key={rest_api_key}&language=ko"
                    nearby_response = requests.get(nearby_url).json()

                    # rating이 4.0 이상인 곳만 필터링
                    filtered_places = [place for place in nearby_response['results']
                                        if place.get('rating', 0) >= 3.0
                                        and not place.get('name', '').endswith(('점', '역', 'station)', '점)'))
                                        and not any(keyword in place.get('name', '') for keyword in excluded_keywords)
                                        and place.get('user_ratings_total', 0) >= 3]
                    if filtered_places:
                        # 필터링된 장소에서 랜덤으로 하나 선택
                        selected_place = random.choice(filtered_places)
                        result.append({
                            'subway_station': location_response['candidates'][0]['name'],
                            'nearby_place': {
                                'name': selected_place['name'],
                                'place_id' : selected_place['place_id'],
                                'rating': selected_place['rating'],
                                'user_ratings_total': selected_place['user_ratings_total']
                            }
                        })
                        end_time = time.time()
                        print("시간 : ", end_time - cur_time)
                        break
                
                    
        if result:
            return JsonResponse({'results': {'category': user_category, 'places': result}})
        else:
            return JsonResponse({'error': 'No suitable places found'})
        
    return JsonResponse({'results': {'error': 'Invalid request method'}})

