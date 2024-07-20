import json, requests, random

from django.shortcuts import redirect
from django.conf import settings
# Create your views here.
def random_test(request):
    with open('station_cd_list.json', 'r', encoding='utf-8') as file:
        station_cd_list = json.load(file)

    # 랜덤으로 하나의 station_cd 선택
    random_station_cd = random.choice(station_cd_list)

    rest_api_key = getattr(settings, 'SUBWAY_KEY')
    return redirect(
        f"http://openapi.seoul.go.kr:8088/{rest_api_key}/json/SearchSTNBySubwayLineInfo/1/5/{random_station_cd}/"
    )