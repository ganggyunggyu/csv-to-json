import requests


def get_coordinates(address):
    
    tmap_url = f"https://apis.openapi.sk.com/tmap/geo/convertAddress?version=1&searchTypCd=OtoN&reqAdd={address}&resCoordType=WGS84GEO"

    
    headers = {
        "accept": "application/json",
        "appKey": "YEWVxfrK4j8xTNQZURJ4z1Te4JTZs26v45fgmfn7"
    }
    response = requests.get(tmap_url, headers=headers)
    if response.status_code == 200:
        result = response.json()  
        
        
        if result.get("ConvertAdd") and result["ConvertAdd"].get("newAddressList"):
            upper_name = result["ConvertAdd"]['upperDistName']
            middle_name = result["ConvertAdd"]['middleDistName']
            new_address = result["ConvertAdd"]["newAddressList"]["newAddress"][0]
            road_name = f'{upper_name} {middle_name} {new_address.get("roadName")}'
            lat = new_address.get("newLat")  
            lon = new_address.get("newLon")  
            

            return road_name, lat, lon
        else:
            print("도로명 주소와 좌표를 찾을 수 없습니다.")
    else:
        print("API 요청 실패")
    return None, None, None

