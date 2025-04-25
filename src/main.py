import os
import json
import re
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv

from get_coordinates import get_coordinates

load_dotenv()

app_key = os.getenv('TAMP_KEY')

tmap_url = "https://apis.openapi.sk.com/tmap/geo/convertAddress?version=1&searchTypCd=NtoO&reqAdd=%EC%84%9C%EC%9A%B8%ED%8A%B9%EB%B3%84%EC%8B%9C%20%EC%96%91%EC%B2%9C%EA%B5%AC%20%EC%8B%A0%EC%A0%95%EB%8F%99%20739%EB%B2%88%EC%A7%80&reqMulti=S&resCoordType=WGS84GEO"

headers = {
    "accept": "application/json",
    "appKey": app_key
}

# 번지 글자 추가
def add_beonji(address):
    return re.sub(r'(\d+(-\d+)?)(?!번지)', r'\1번지', address)

# 호수 분리 (**동 **호)
def extract_ho(address):
    match = re.search(r'(\d+[가-힣]*호)', address)
    return match.group(0) if match else None

# 파일 이름 및 경로 설정
file_name = 'seoul-yangcheon'
csv_file_path = f'./csv/{file_name}.csv'

# csv파일 변수에 할당
df = pd.read_csv(csv_file_path, encoding='cp949')

# 지번 주소 불필요한 정보 제거 및 "번지" 추가
df['address_jibun'] = df['소재지'].copy()
df['address_jibun'] = df['address_jibun'].apply(add_beonji)
df['address_jibun'] = df['address_jibun'].str.replace(r'-\*+', '', regex=True)

df.rename(columns={
    '주택유형': 'type',
    '건축년도': 'year',
    '연면적(제곱미터)': 'area'
}, inplace=True)

df['ho'] = df['address_jibun'].apply(extract_ho)

df['address_jibun'] = df['address_jibun'].apply(lambda x: re.sub(r'(\d+[가-힣]*호)', '', x).strip())

# 컬럼에 좌표, 도로명 주소 추가
df['latitude'] = None
df['longitude'] = None
df['address_road'] = None

for index, row in tqdm(df.iterrows(), total=len(df), desc="좌표 변환 중"):
    address_jibun = row['address_jibun']

    road_name, lat, lon = get_coordinates(address_jibun)
    df.at[index, 'latitude'] = lat
    df.at[index, 'longitude'] = lon
    df.at[index, 'address_road'] = road_name


df.to_csv(f'{file_name}-with-coordinates.csv', index=False, encoding='utf-8')


json_data = df[['address_jibun', 'address_road', 'type', 'year', 'area', 'ho', 'latitude', 'longitude']].to_dict(orient='records')
json_string = json.dumps(json_data, ensure_ascii=False, indent=2)

with open(f'{file_name}-with-coordinates.json', 'w', encoding='utf-8') as f:
    f.write(json_string)

print("✅ 좌표 변환 완료! CSV & JSON 저장됨.")
