from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX


router = APIRouter(tags=["4-1.道路資訊(Website)"],prefix="/Website/Information/Road")
collection_parking_info = MongoDB.getCollection("traffic_hero","information_parking_city_parking_info")
collection_parking_num = MongoDB.getCollection("traffic_hero","information_parking_city_parking_num")

@router.put("/CityCarPark_ParkingInfo",summary="【Update】道路資訊-指定縣市停車場基本資料")
async def CityCarPark_ParkingInfo(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 指定[縣市]停車場基本資料\n
            https://tdx.transportdata.tw/api-service/swagger/basic/945f57da-f29d-4dfd-94ec-c35d9f62be7d#/CityCarPark/ParkingApi_CarPark \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證

    return updateInfo()
def updateInfo():
    collection_parking_info.drop() # 刪除該collection所有資料
    documents = []

    County = ['Taipei','Taoyuan','Taichung','Tainan','Kaohsiung','Keelung','Hsinchu','MiaoliCounty','NantouCounty','ChiayiCounty','Chiayi','PingtungCounty','YilanCounty','HualienCounty','TaitungCounty','KinmenCounty','LienchiangCounty']
    try:
        for county in County:
            BasicInfoUrl = f"https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/CarPark/City/{county}?%24format=JSON" # 取得資料來源網址
            BasicInfoData = TDX.getData(BasicInfoUrl) # 取得資料
            
            for data in BasicInfoData['CarParks']:
                document = {
                    "City": data['City'],
                    "CarParkID": data['CarParkID'],
                    "CarParkName": data['CarParkName']['Zh_tw'],
                    "Latitude": data['CarParkPosition']['PositionLat'],
                    "Longitude": data['CarParkPosition']['PositionLon'],
                    "Address": data['Address'],
                    "FareDescription": data['FareDescription'],
                    "TotalSpace": getParkingTotalSpace(data['CarParkID'],data['CityCode'])
                }
                documents.append(document)
    except Exception as e:
        print(e)

    collection_parking_info.insert_many(documents)

    return f"已更新筆數:{collection_parking_info.count_documents({})}"

# 從 information_parking_city_parking_num 中找出各個縣市停車場所對應的停車位數
def getParkingTotalSpace(CarParkID:str,CountyCodes:str):
    ParkingNumData = collection_parking_num.find_one({"CarParkID":CarParkID,"County":CountyCodes})
    return ParkingNumData['TotalSpaces'] if(ParkingNumData != None) else 0