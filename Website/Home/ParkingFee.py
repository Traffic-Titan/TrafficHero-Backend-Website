from fastapi import APIRouter, Depends , HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
from pydantic import BaseModel
import requests
import Function.Area as Area
import time
import httpx
import asyncio
from typing import Optional

router = APIRouter(tags=["1.首頁(Website)"],prefix="/Website/Home")

collection = MongoDB.getCollection("traffic_hero","parking_fee") # 連線MongoDB

@router.put("/ParkingFee/SystemStatus", summary="【Update】各縣市路邊停車費-系統狀態")
async def updateParkingFee_SystemStatusAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX) - 路邊停車費查詢API
                https://tdx.transportdata.tw/api-service/parkingFee \n
    二、Input \n
            1. 類別: C：汽車；M：機車；O：其他(如拖車)
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    return await updateParkingFee_SystemStatus()
    
async def updateParkingFee_SystemStatus():
    test_data = list(collection.find({"area": "test"},{"_id":0}))[0] # 取得資料庫內容
    data = list(collection.find({},{"_id":0}))
    for d in data:
        await process(d, test_data)
        
    return {"message": "更新成功"}

async def process(d, test_data):
    area = d["area"]
    
    try:
        if area != "test":
            url = d['url']
            url = url.replace("Insert_CarID", test_data["license_plate_number"]) # 取代車牌號碼
            url = url.replace("Insert_CarType", test_data["type"]) # 取代車輛類別
            with httpx.Client(timeout = 2) as client: # timeout
                response = client.get(url) # 發送請求
                dataAll = response.json()
            
            collection.update_one({"area": area},{"$set": {"status": True}}) # 更新狀態
            
    except requests.Timeout:
        collection.update_one({"area": area},{"$set": {"status": False}}) # 更新狀態
        print(f"Request timed out for area {area}, using default data") # 請求逾時
    except Exception as e:
        collection.update_one({"area": area},{"$set": {"status": False}}) # 更新狀態
        print(f"Error processing data for area {area}: {e}") # 其他錯誤
    
