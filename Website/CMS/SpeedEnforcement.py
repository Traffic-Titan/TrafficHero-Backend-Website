from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from PIL import Image
import os
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
import Website.CMS.MainContent as CMS_MainContent
from datetime import datetime, timedelta
import requests

router = APIRouter(tags=["3.即時訊息推播(Website)"],prefix="/Website/CMS")

collection_cms = MongoDB.getCollection("traffic_hero","cms_speed_enforcement")

@router.put("/SpeedEnforcement", summary="【Update】即時訊息推播-測速執法設置點")
async def getSpeedEnforcementAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 政府資料開放平臺 - 測速執法設置點
                https://data.gov.tw/dataset/7320 \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    return await getSpeedEnforcement()

async def getSpeedEnforcement():
    # 取得剩餘停車位數
    url = "https://od.moi.gov.tw/api/v1/rest/datastore/A01010000C-000674-011" 
    data = requests.get(url).json()
    
    
    collection = MongoDB.getCollection("traffic_hero","speed_enforcement") # 取得MongoDB的collection
    collection.delete_many({}) # 清空collection
    collection.insert_many(data["result"]["records"][1:]) # 第一筆資料為欄位名稱，故不加入

    # 轉換時區(待模組化)
    import pytz
    taipei_timezone = pytz.timezone('Asia/Taipei')
    current_time = datetime.now(taipei_timezone)

    # count = 0
    documents = []
    for d in collection.find({},{"_id":0}):
        # count += 1
        # print(f"更新第{count}筆資料")
        documents.append({
                "type": "測速執法設置點",
                "icon": "https://blog.eddie.tw/speed_enforcement.png",
                "content": [
                    {
                        "text": ["測速照相"],
                        "color": ["#FFFFFF"]
                    },
                    {
                        "text": [d["limit"],"km/h"],
                        "color": ["#FFFFFF","#FFFFFF"]
                    }
                ],
                "voice": f"前方有測速照相，限速{d['limit']}公里",
                "location": {
                    "longitude": float(d["Longitude"]),
                    "latitude": float(d["Latitude"])
                },
                "direction": d["direct"],
                "distance": 1,
                "priority": "Demo", # Demo
                "speed_limit": d["limit"],
                "start": current_time,
                "end": current_time + timedelta(minutes = 10),
                "active": True,
                "id": "string"
        })

    collection_cms.insert_many(documents)
    
    return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}