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

@router.put("/Shoulder", summary="【Update】即時訊息推播-高速公路路肩開放狀態")
async def getStauts(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 即時路況 - 交通部高速公路局
                https://1968.freeway.gov.tw/ \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證

    # 取得1968資料
    data = requests.get(f'https://1968.freeway.gov.tw/api/getShoulder?freewayid=0&expresswayid=0').json()
    
    collection = await MongoDB.getCollection("traffic_hero","freeway_shoulder_status") # 取得MongoDB的collection
    await collection.delete_many({}) # 清空collection
    await collection.insert_many(data["response"])
    
    return {"message": f"更新成功，總筆數:{await collection.count_documents({})}"}
    
    # for result in await collection.find({}, {"_id": 0}): # Demo
    #     if "available" in result:
    #         status = parkingLevelToStatus(result['parkingLevel'])
    #         content = {
    #             "type": "高速公路服務區停車位狀態",
    #             "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/ROC_Taiwan_Area_National_Freeway_Bureau_Logo.svg/200px-ROC_Taiwan_Area_National_Freeway_Bureau_Logo.svg.png",
    #             "content": [
    #                 {
    #                     "text": [f"{result['service_name']}"],
    #                     "color": ["#FFFFFF"]
    #                 },
    #                 {
    #                     "text": [f"狀態:",status],
    #                     "color": ["#FFFFFF","#FFFFFF"]
    #                 },
    #                 {
    #                     "text": [f"尚有{result['available']}格停車位"],
    #                     "color": ["#FFFFFF"]
    #                 }
    #             ],
    #             "voice": f"前方{result['service_name']}，目前還有{result['available']}格停車位，停車位{status}",
    #             "longitude": "121.000000", # Demo
    #             "latitude": "25.000000", # Demo
    #             "direction": "string", # Demo
    #             "distance": 2.5, # Demo
    #             "priority": "1", # Demo
    #             "start": datetime.now(),
    #             "end": datetime.now() + timedelta(hours=10000), # Demo
    #             "active": True,
    #             "id": "string"
    #             }
    #     else:
    #         content = {
    #             "type": "高速公路服務區停車位狀態",
    #             "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/ROC_Taiwan_Area_National_Freeway_Bureau_Logo.svg/200px-ROC_Taiwan_Area_National_Freeway_Bureau_Logo.svg.png",
    #             "content": [
    #                 {
    #                     "text": [f"{result['service_name']}"],
    #                     "color": ["#FFFFFF"]
    #                 },
    #                 {
    #                     "text": [f"狀態:",status],
    #                     "color": ["#FFFFFF","#FFFFFF"]
    #                 }
    #             ],
    #             "voice": f"前方{result['service_name']}，停車位{status}",
    #             "longitude": "121.000000", # Demo
    #             "latitude": "25.000000", # Demo
    #             "direction": "string", # Demo
    #             "distance": 2.5, # Demo
    #             "priority": "1", # Demo
    #             "start": datetime.now(),
    #             "end": datetime.now() + timedelta(hours=10000), # Demo
    #             "active": True,
    #             "id": "string"
    #             }

    #     CMS.createContent("car", content)
