"""
1. 目前先將統一抓取各縣市資料，未來可考慮改成抓取單一縣市資料
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import Service.TDX as TDX
from Main import MongoDB # 引用MongoDB連線實例
from typing import Optional, List, Union
import json
from pydantic import BaseModel, HttpUrl
import hashlib
from collections import OrderedDict
import Function.Time as Time
import Function.Link as Link
import Function.Logo as Logo

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")

collection = MongoDB.getCollection("traffic_hero","news_mrt")

@router.put("/MRT",summary="【Update】最新消息-捷運")
async def updateNewsAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX) - 捷運最新消息資料
                https://tdx.transportdata.tw/api-service/swagger/basic/268fc230-2e04-471b-a728-a726167c1cfc#/Metro/MetroApi_News_2106 \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    return updateNews()

def updateNews():
    dataToDatabase("TaipeiCity") # 臺北捷運
    dataToDatabase("TaoyuanCity") # 桃園捷運
    dataToDatabase("KaohsiungCity") # 高雄捷運
            
    return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}

def dataToDatabase(area: str):
    try:
        url = Link.get("traffic_hero", "news_source", "mrt", area) # 取得資料來源網址
        data = TDX.getData(url)
        
        documents = []
        logo_url = Logo.get("mrt", area) # 取得Logo
        for d in data["Newses"]: # 將資料整理成MongoDB的格式
            document = {
                "area": area,
                "news_id": d['NewsID'],
                "title": d['Title'],
                "news_category": numberToText(d['NewsCategory']),
                "description": d['Description'],
                "news_url": d['NewsURL'] if 'NewsURL' in d else "",
                "update_time": Time.format(d['UpdateTime']),
                "logo_url": logo_url
            }
            documents.append(document)

        collection.delete_many({"area": area}) # 刪除該區域所有資料
        collection.insert_many(documents) # 將資料存入MongoDB
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}

def numberToText(number : int):
    match number:
        case 1:
            return "最新消息"
        case 2:
            return "新聞稿"
        case 3:
            return "營運資訊"
        case 4:
            return "轉乘資訊"
        case 5:
            return "活動訊息"
        case 6:
            return "系統公告"
        case 7:
            return "新服務上架"
        case 8:
            return "API修正"
        case 9:
            return "來源異常"
        case 10:
            return "資料更新"
        case 99:
            return "其他"