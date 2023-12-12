from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

router = APIRouter(tags=["4-1.道路資訊(Website)"],prefix="/Website/Information/Road")

@router.put("/CityCarPark_ParkingNum",summary="【Update】道路資訊-指定縣市停車場車位數量")
async def CityCarPark_ParkingNum(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 指定[縣市]之停車場車位數資料\n
            https://tdx.transportdata.tw/api-service/swagger/basic/945f57da-f29d-4dfd-94ec-c35d9f62be7d#/CityCarPark/ParkingApi_ParkingSpace\n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證

    return await updateInfo()

async def updateInfo():
    collection = await MongoDB.getCollection("traffic_hero","information_parking_city_parking_num")
    
    collection.drop() # 刪除該collection所有資料
    documents = []

    County = ['Taipei','Taoyuan','Taichung','Tainan','Kaohsiung','Keelung','Hsinchu','MiaoliCounty','NantouCounty','ChiayiCounty','Chiayi','PingtungCounty','YilanCounty','HualienCounty','TaitungCounty','KinmenCounty','LienchiangCounty']
    try:
        for county in County:
            ParkingNumUrl = f"https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingSpace/City/{county}?%24format=JSON" # 取得資料來源網址
            ParkingNumData = TDX.getData(ParkingNumUrl) # 取得資料
            for data in ParkingNumData['ParkingSpaces']:
                document = {
                    "County": ParkingNumData['AuthorityCode'],
                    "CarParkID": data['CarParkID'],
                    "CarParkName": data['CarParkName']['Zh_tw'],
                    "TotalSpaces": data['TotalSpaces'],
                    "MaxAllowedHeight": data['Spaces'][0]['MaxAllowedHeight'] if("MaxAllowedHeight" in data['Spaces'][0]) else "無說明",
                    "MaxAllowedWeight": data['Spaces'][0]['MaxAllowedWeight'] if("MaxAllowedWeight" in data['Spaces'][0]) else "無說明",
                    "HasChargingPoint":"有充電樁" if(data['Spaces'][0]['HasChargingPoint'] == 1) else "無充電樁"
                }
                documents.append(document)
    except Exception as e:
        print(e)

    collection.insert_many(documents)

    return f"已更新筆數:{collection.count_documents({})}"