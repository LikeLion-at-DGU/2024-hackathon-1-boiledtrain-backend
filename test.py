import json

# JSON 파일 경로
input_file_path = 'subwayinfo.json'
output_file_path = 'mk_data.json'

# 필터링할 호선 목록
target_lines = {"04호선", "05호선", "08호선", "우이신설경전철", "신림선", "서해선"}

# JSON 파일 읽기
with open(input_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# "DATA" 배열 추출
data_array = data.get('DATA', [])

# 필터링 및 필요한 데이터 추출
filtered_data = [
    {
        'line_num': entry.get('line_num'),
        'station_cd': entry.get('station_cd'),
        'station_nm': entry.get('station_nm')
    }
    for entry in data_array
    if entry.get('line_num') in target_lines
]

# 필터링된 데이터 저장
with open(output_file_path, 'w', encoding='utf-8') as file:
    json.dump(filtered_data, file, ensure_ascii=False, indent=4)

print(f'필터링된 데이터가 {output_file_path}에 저장되었습니다.')
