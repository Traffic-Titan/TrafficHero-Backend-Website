from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

router = APIRouter(tags=["4-1.道路資訊(Website)"],prefix="/Website/Information/Road")

@router.put("/ParkingSpot/Taichung",summary="【Update】路邊停車位基本資料-臺中市")
async def update(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
             1.  臺中市政府資料開放平台 - 臺中市路邊停車收費路段
                https://opendata.taichung.gov.tw/dataset/f4ae2e75-b81e-445b-9119-765c4ed84c0f \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證

    try:
        url = "https://datacenter.taichung.gov.tw/swagger/OpenData/556d6519-3424-4a02-b46c-d6b24352143c"
        response = requests.get(url)
        data = response.json()
        
        collection = await MongoDB.getCollection("traffic_hero","information_parking_on_street_taichung")
        collection.drop()
        collection.insert_many(data) # 將資料存入MongoDB
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}

    return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}


@router.put("/ParkingSpot/Availability/Taichung",summary="【Update】路邊停車位即時剩餘資料-臺中市")
async def update(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
             1.  臺中市政府資料開放平台 - 臺中市路邊剩餘車位
                https://opendata.taichung.gov.tw/dataset/d7310e46-1dd2-4d25-800b-8d69d0e2d5fe \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證

    try:
        url = "https://datacenter.taichung.gov.tw/swagger/OpenData/791a8a4b-ade6-48cf-b3ed-6c594e58a1f1"
        response = requests.get(url)
        data = response.json()
        
        collection = await MongoDB.getCollection("traffic_hero","information_parking_on_street_availability_taichung")
        collection.drop()
        collection.insert_many(data) # 將資料存入MongoDB
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}

    return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}