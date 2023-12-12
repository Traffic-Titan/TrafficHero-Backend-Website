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

@router.put("/LocalRoad",summary="【Update】最新消息-地區道路")
async def updateNewsAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX) - 地區道路最新消息資料
                https://tdx.transportdata.tw/api-service/swagger/basic/7f07d940-91a4-495d-9465-1c9df89d709c#/CityTraffic/Live_News_City \n
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
    collection = await MongoDB.getCollection("traffic_hero","news_local_road")
    
    areas = ["TaichungCity","TainanCity","PingtungCounty","YilanCounty","MiaoliCounty","ChanghuaCounty","YunlinCounty","NewTaipeiCity", "ChiayiCity","TaoyuanCity"]
    
    for area in areas: # 依照區域更新資料
        await dataToDatabase(area)

    return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}
    
async def dataToDatabase(area: str):
    collection = await MongoDB.getCollection("traffic_hero","news_local_road")
    
    try:
        url = Link.get("traffic_hero", "news_source", "local_road", area) # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        
        documents = []
        logo_url = Logo.get("local_road", area) # 取得Logo
        for d in data["Newses"]: # 將資料轉換成MongoDB格式
            document = {
                "area": area,
                "news_id": d['NewsID'],
                "title": d['Title'],
                "news_category": await numberToText(d['NewsCategory']),
                "description": d['Description'],
                "news_url": "", # 因此資料集的新聞網址有問題，所以以空值取代，讓前端可以直接顯示Description
                "update_time": Time.format(d['UpdateTime']),
                "logo_url": logo_url
            }
            documents.append(document)
            
        collection.delete_many({"area": area}) # 刪除該區域所有資料
        collection.insert_many(documents) # 將資料存入MongoDB
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}

async def numberToText(number : int):
    match number:
        case 1:
            return "交管措施"
        case 2:
            return "事故"
        case 3:
            return "壅塞"
        case 4:
            return "施工"
        case 99:
            return "其他"
        case _:
            return "其他"
