from django.shortcuts import render
from django.http import JsonResponse
import requests, json, random
from django.conf import settings
from rest_framework import viewsets, mixins
from datetime import datetime


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

                    nearby_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=1000&language=kr&type={category}&key={rest_api_key}"
                    nearby_response = requests.get(nearby_url).json()

                    # rating이 4.0 이상인 곳만 필터링
                    filtered_places = [place for place in nearby_response['results']
                                        if place.get('rating', 0) >= 4.0
                                        and not place.get('name', '').endswith(('점', '역', 'station)', '점)'))
                                        and not place.get('name', '').startswith(("Paik's", 'Dunkin', '배스킨라빈스', 'KFC', 'Outback Steakhouse', "Domino's", 'Bonjuk', 'Burger King', '네네치킨', 'Pelicana Chicken', 'Bonjug', 'Pizza Maru'))
                                        and '파리바게' not in place.get('name', '')
                                        and 'Paris Baguette' not in place.get('name', '')
                                        and '뚜레쥬르' not in place.get('name', '')
                                        and 'Tous Les Jours' not in place.get('name', '')
                                        and 'Starbucks' not in place.get('name', '')
                                        and '스타벅스' not in place.get('name', '')
                                        and 'LOTTERIA' not in place.get('name', '')
                                        and '설빙' not in place.get('name', '')
                                        and 'Sulbing' not in place.get('name', '')
                                        and 'Hollys' not in place.get('name', '')
                                        and "Holly's" not in place.get('name', '')
                                        and '인쌩맥주' not in place.get('name', '')
                                        and '장미맨숀' not in place.get('name', '')
                                        and 'Ediya' not in place.get('name', '')
                                        and 'Pizza School' not in place.get('name', '')
                                        and 'Daiso' not in place.get('name', '')
                                        and 'KyoChon' not in place.get('name', '')
                                        and 'Kyochon' not in place.get('name', '')
                                        and "Mom's Touch" not in place.get('name', '')
                                        and '스터디카페' not in place.get('name', '')
                                        and '키즈카페' not in place.get('name', '')
                                        and '7080' not in place.get('name', '')
                                        and '상가' not in place.get('name', '')
                                        and '프라자' not in place.get('name', '')
                                        and 'plaza' not in place.get('name', '')
                                        and 'Pizza Hut' not in place.get('name', '')
                                        and 'Compose Coffee' not in place.get('name', '')
                                        and 'Mega Coffee' not in place.get('name', '')
                                        and 'Krispy Kreme' not in place.get('name', '')
                                        and '로봇카페' not in place.get('name', '')
                                        and '무인카페' not in place.get('name', '')
                                        and '커스텀커피' not in place.get('name', '')
                                        and 'Chicken Mania' not in place.get('name', '')
                                        and 'BHC' not in place.get('name', '')
                                        and 'BBQ' not in place.get('name', '')
                                        and 'The Coffee Bean' not in place.get('name', '')
                                        and '교촌' not in place.get('name', '')
                                        and '피씨카페' not in place.get('name', '')
                                        and 'Twosome Place' not in place.get('name', '')
                                        and '샵' not in place.get('name', '')
                                        and '메가커피' not in place.get('name', '')
                                        and '메가엠지씨커피' not in place.get('name', '')
                                        and 'Fitness' not in place.get('name', '')
                                        and '멕시카나' not in place.get('name', '')
                                        and 'Tom N Toms' not in place.get('name', '')
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
                    'nearby_place': selected_place
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
# M.K 파트
def choose_place(request):
    # 사용자가 프론트 인터페이스에 입력한 장소 이름을 받아와서 구글 api를 통해 검색
    rest_api_key = getattr(settings, 'MAP_KEY')
    #프론트에서 받아올 부분
    subway_station = "돌곶이역"
    place = "길음 롯데리아"
    location_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={place}&key={rest_api_key}&language=kr"
    location_response = requests.get(location_url).json()
    
    return JsonResponse(location_response)

def add_place(request):

    # choose_place 에서 선택한 장소의 id 를 전달받아서 세부 정보를 가져온 후 db 에 json 형태로 저장
    rest_api_key = getattr(settings, 'MAP_KEY')
    #프론트에서 받아올 부분
    place_id = "경춘선 숲길"
    location_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={place}&key={rest_api_key}&language=kr"
    location_response = requests.get(location_url).json()
    
    # if location_response['candidates']:
    #     location = location_response['candidates'][0]['geometry']['location']
    #     lat = location['lat']
    #     lng = location['lng']
    # detail_url = f"https://maps.googleapis.com/maps/api/place/details/json?fields=name%2Crating%2Cformatted_phone_number&place_id=ChIJN1t_tDeuEmsRUsoyG83frY4&key={rest_api_key}"
    # detail_response = requests.get(detail_url).json()
    return JsonResponse(location_response)

class Place(viewsets.ModelViewSet):
    pass
    # 장소 정보를 추가, 삭제, 출력