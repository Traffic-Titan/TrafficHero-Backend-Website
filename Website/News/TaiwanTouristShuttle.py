from fastapi import APIRouter, Depends, HTTPException
import Service.TDX as TDX
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from fastapi import APIRouter
import Service
import re
import csv
import os
import json
import urllib.request as request
from typing import Optional
from Main import MongoDB # 引用MongoDB連線實例
import Function.Time as Time
import Function.Link as Link
import Function.Area as Area
import Function.Logo as Logo
import time

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")

@router.put("/TaiwanTouristShuttle",summary="【Update】最新消息-臺灣好行公車")
async def updateNewsAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())): 
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX) - 臺灣好行公車最新消息資料 v2
                https://tdx.transportdata.tw/api-service/swagger/basic/cd0226cf-6292-4c35-8a0d-b595f0b15352#/Tourism/TaiwanTripBusApi_News_2268 \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    return await updateNews()
    
async def updateNews():
    collection = await MongoDB.getCollection("traffic_hero","news_taiwan_tourist_shuttle")
    
    for area in Area.english: # 依照區域更新資料
        await dataToDatabase(area)

    return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}
    
async def dataToDatabase(area: str):
    collection = await MongoDB.getCollection("traffic_hero","news_taiwan_tourist_shuttle")
    
    try:
        url = Link.get("traffic_hero", "news_source", "taiwan_tourist_shuttle", "All") # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        
        documents = []
        logo_url = Logo.get("taiwan_tourist_shuttle", "All") # 取得Logo
        for d in data: # 將資料轉換成MongoDB格式
            document = {
                "area": "All",
                "news_id": d['NewsID'],
                "title": d['Title'],
                "news_category": d['NewsCategory'],
                "description": d['Description'],
                "news_url": d['NewsURL'] if 'NewsURL' in d else "",
                "update_time": Time.format(d['SrcUpdateTime']),
                "logo_url": logo_url
            }
            documents.append(document)
            
        collection.drop() # 刪除該collection所有資料
        collection.insert_many(documents) # 將資料存入MongoDB
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}
