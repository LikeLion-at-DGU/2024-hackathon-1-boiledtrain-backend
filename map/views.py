from django.shortcuts import render
from django.http import JsonResponse
import requests, json, random, os
from django.conf import settings
from rest_framework import viewsets, mixins
from datetime import datetime
import time, json
from django.views.decorators.csrf import csrf_exempt

BASE_URL = 'http://localhost:8000/'

excluded_keywords = [
            'Dunkin', '배스킨라빈스', 'KFC', 'Outback Steakhouse', "Domino's", 'Bonjuk', 'Burger King',
            '네네치킨', 'Pelicana Chicken', 'Bonjug', 'Pizza Maru', '파리바게', 'Paris Baguette', '뚜레쥬르', 'Tous Les Jours',
            'Starbucks', '스타벅스', 'LOTTERIA', '설빙', 'Sulbing', 'Hollys', "Holly's", 'Ediya', 
            'Pizza School', 'Daiso', 'KyoChon', 'Kyochon', "Mom's Touch", '스터디카페', '키즈카페', '7080', '상가', 
            '프라자', 'plaza', 'Pizza Hut', 'Compose Coffee', 'Mega Coffee', 'Krispy Kreme', '로봇카페', '무인카페', 
            '커스텀커피', 'Chicken Mania', 'BHC', 'BBQ', 'The Coffee Bean', '교촌', '피씨카페', 'Twosome Place', '샵', 
            '메가커피', '메가엠지씨커피', 'Fitness', '멕시카나', 'Tom N Toms', 'Puradak Chicken', 'COFFEE BAY', '페리카나', 
            'paris baguette', 'Pascucci', 'Gongcha', "Paik's", '역전커피', '이디야', '치킨매니아', '신의주찹쌀순대', 'PARIS BAGUETTE', '파리바케', 
            '본죽', '멕시칸치킨', '김가네', '빽다방', '던킨도너츠', 'EDIYA', '와플대학', '뚜레주르', '탐앤탐스', '주차장', '식품관', '나리폰', '환전',
            '구로학습지원센터','미소야'
        ]

change_category_ko = {
            'bakery': '베이커리',
            'book_store': '서점',
            'cafe': '카페',
            'department_store': '쇼핑몰',
            'museum': '박물관 및 전시회',
            'restaurant': '맛집'
        }

change_category_eng = {
    '베이커리': 'bakery',
    '서점': 'book_store',
    '카페': 'cafe',
    '쇼핑몰': 'department_store',
    '박물관 및 전시회': 'museum',
    '맛집': 'restaurant'
}

###################################################
# 랜덤 여행

def search_places_random(request):
    if request.method == "GET":
        with open('station_nm_list.json', 'r', encoding='utf-8') as file:
            station_nm_list = json.load(file)
        with open('place_category.json', 'r', encoding='utf-8') as file:
            categories = json.load(file)['places']
        random.shuffle(station_nm_list)
        random.shuffle(categories)

        rest_api_key = getattr(settings, 'MAP_KEY')
        cur_time = time.time()

        i = 0  # station_nm_list 인덱스 초기화

        while True:
            if i >= len(station_nm_list):
                return JsonResponse({'error': 'No suitable place found'})
            
            if station_nm_list[i] == "서울역":
                subway = station_nm_list[i]
            else:
                subway = station_nm_list[i] + "역"

            # json 으로 출력할 역 이름
            result_subway = station_nm_list[i]
            i = i + 1
            
            location_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?fields=formatted_address%2Cname%2Crating%2Copening_hours%2Cgeometry&input={subway}&inputtype=textquery&key={rest_api_key}&language=ko"
            location_response = requests.get(location_url).json()

            if location_response['candidates']:
                location = location_response['candidates'][0]['geometry']['location']
                lat = location['lat']
                lng = location['lng']

                selected_places_ids = set()
                test = []
                success = True

                count = 0  # 장소 카운트 초기화
                j = 0  # categories 인덱스 초기화

                while count < 3:  # 3곳의 장소가 선택될 때까지 반복
                    if j >= len(categories):
                        success = False
                        break

                    category = categories[j]
                    j += 1

                    # if category == "bar":
                    #     current_hour = datetime.now().hour
                    #     if not (15 <= current_hour <= 22):
                    #         continue

                    nearby_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=1000&language=ko&type={category}&lanbuage=ko&key={rest_api_key}&language=ko"
                    nearby_response = requests.get(nearby_url).json()

                    filtered_places = [place for place in nearby_response['results']
                                        if place.get('rating', 0) >= 3.5
                                        and not place.get('name', '').endswith(('점', '역', 'station)', '점)'))
                                        and not any(keyword in place.get('name', '') for keyword in excluded_keywords)
                                        and place.get('user_ratings_total', 0) >= 3
                                        and place.get('place_id') not in selected_places_ids]

                    if filtered_places:
                        selected_place = random.choice(filtered_places)
                        selected_places_ids.add(selected_place['place_id'])

                        test.append({
                            'category': change_category_ko.get(category, category),
                            'nearby_place': {
                                'name': selected_place['name'],
                                'place_id': selected_place['place_id'],
                                'rating': selected_place['rating'],
                                'user_ratings_total': selected_place['user_ratings_total'],
                                # 'photo_reference' : selected_place['photos'][0]['photo_reference']
                            }
                        })
                        if 'photos' in selected_place:
                            test[len(test) - 1]['nearby_place']['photo_reference'] = selected_place['photos'][0]['photo_reference']
                        count += 1  # 장소가 추가될 때마다 카운트 증가

                if success:
                    end_time = time.time()
                    print("시간 : ", end_time - cur_time)
                    return JsonResponse({'subway_station': result_subway, 'places': test})

            else:
                return JsonResponse({'error': 'Place not found'})
    return JsonResponse({'error': 'Invalid request method'})
###################################################################
# 목적 여행
@csrf_exempt
def search_places_category(request):
    if request.method == "POST":

        choose_category = json.loads(request.body)
        if choose_category is None:
            return JsonResponse({'error': 'Category not specified'})
        
        ko_category = choose_category['category']

        # 사용자가 선택한 카테고리를 영어로 변환
        user_category = change_category_eng.get(ko_category, ko_category)
        
        result = []
        i = 0 # 인덱스
        used_place_ids = set()  # 이미 선택된 장소 ID를 추적

        with open('station_nm_list.json', 'r', encoding='utf-8') as file:
            station_nm_list = json.load(file)
        random.shuffle(station_nm_list)
        
        for _ in range(3):  # 3번 반복
            while True:  # 조건에 맞는 장소가 나올 때까지 반복
                cur_time = time.time()
                # 지하철 역을 새로 찾을 때마다 장소 카운트 초기화
                cnt = 0
                if station_nm_list[i] == "서울역":
                    subway = station_nm_list[i]
                else:
                    subway = station_nm_list[i] + "역"

                result_subway = station_nm_list[i]
                i = i + 1

                # 지하철역의 이름을 추출해서 장소 검색
                rest_api_key = settings.MAP_KEY
                location_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?fields=formatted_address%2Cname%2Crating%2Copening_hours%2Cgeometry&input={subway}&inputtype=textquery&key={rest_api_key}&language=ko"
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
                                        if place.get('rating', 0) >= 3.5
                                        and not place.get('name', '').endswith(('점', '역', 'station)', '점)'))
                                        and not any(keyword in place.get('name', '') for keyword in excluded_keywords)
                                        and place.get('user_ratings_total', 0) >= 3]

                    # 중복된 장소 ID가 아닌 것만 선택
                    filtered_places = [place for place in filtered_places if place['place_id'] not in used_place_ids]
                    
                    if filtered_places:
                        # 필터링된 장소에서 랜덤으로 하나 선택
                        selected_place = random.choice(filtered_places)
                        used_place_ids.add(selected_place['place_id'])
                        # 장소를 찾았으면 카운트 1 증가
                        cnt = cnt + 1
                        # 추가 카테고리의 장소 검색
                        with open('place_category.json', 'r', encoding='utf-8') as f:
                            categories = json.load(f)['places']
                        additional_places = []
                        selected_categories = set()  # 선택된 카테고리를 추적

                        for category in categories:
                            if category != user_category and category not in selected_categories:
                                additional_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=1000&language=ko&type={category}&key={rest_api_key}&language=ko"
                                additional_response = requests.get(additional_url).json()
                                if additional_response['results']:
                                    additional_filtered = [place for place in additional_response['results']
                                                            if place.get('rating', 0) >= 3.5
                                                            and not place.get('name', '').endswith(('점', '역', 'station)', '점)'))
                                                            and not any(keyword in place.get('name', '') for keyword in excluded_keywords)
                                                            and place.get('user_ratings_total', 0) >= 3
                                                            and place['place_id'] not in used_place_ids]
                                    if additional_filtered:
                                        selected_categories.add(category)
                                        additional_place = random.choice(additional_filtered)

                                        additional_places.append({
                                            'category': change_category_ko.get(category,category),
                                            'name': additional_place['name'],
                                            'place_id': additional_place['place_id'],
                                            'rating': additional_place['rating'],
                                            'user_ratings_total': additional_place['user_ratings_total']
                                            # 'photo_reference' : additional_place['photos'][0]['photo_reference']
                                        })
                                        if 'photos' in additional_place:
                                            # 총 카운트에서 1 감소한 인덱스에 접근
                                            additional_places[cnt - 1]['photo_reference'] = additional_place['photos'][0]['photo_reference']
                                        used_place_ids.add(additional_place['place_id'])

                                        
                                        # 장소 카운트를 1 증가
                                        cnt = cnt + 1
                                        # 장소 카운트가 3개가 넘어가면 break
                                        if cnt >= 3: 
                                            break

                        result.append({
                            'subway_station': result_subway,
                            'nearby_place': {
                                'name': selected_place['name'],
                                'place_id': selected_place['place_id'],
                                'rating': selected_place['rating'],
                                'user_ratings_total': selected_place['user_ratings_total'],
                            },
                            'additional_places': additional_places
                        })
                        if 'photos' in selected_place:
                                result[len(result) - 1]['nearby_place']['photo_reference'] = selected_place['photos'][0]['photo_reference']
                        end_time = time.time()
                        print("시간 : ", end_time - cur_time)
                        break
                
        if result:
            return JsonResponse({'category' : ko_category, 'places': result})
        else:
            return JsonResponse({'error': 'No suitable places found'})
        
    return JsonResponse({'results': {'error': 'Invalid request method'}})
