from fastapi import APIRouter, Depends, HTTPException
import Service.TDX as TDX
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from fastapi import APIRouter
import urllib.request as request
from typing import Optional
from Main import MongoDB # 引用MongoDB連線實例
import Function.Time as Time
import Function.Link as Link
import Function.Area as Area
import Function.Logo as Logo
import time

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")

@router.put("/Bus",summary="【Update】最新消息-公車")
async def updateNewsAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())): 
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX) - 市區公車最新消息資料
                https://tdx.transportdata.tw/api-service/swagger/basic/2998e851-81d0-40f5-b26d-77e2f5ac4118#/CityBus/CityBusApi_News_2044 \n
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
    collection = await MongoDB.getCollection("traffic_hero","news_bus")
    
    for area in Area.english: # 依照區域更新資料
        await dataToDatabase(area)

    return {"message": f"更新成功，總筆數:{await collection.count_documents({})}"}
    
async def dataToDatabase(area: str):
    collection = await MongoDB.getCollection("traffic_hero","news_bus")
    
    try:
        url = Link.get("traffic_hero", "news_source", "bus", area) # 取得資料來源網址
        data = TDX.getData(url) # 取得資料

        documents = []
        logo_url = await Logo.get("bus", area) # 取得Logo
        for d in data: # 將資料轉換成MongoDB格式
            document = {
                "area": area,
                "news_id": d['NewsID'],
                "title": d['Title'],
                "news_category": await numberToText(d['NewsCategory']),
                "description": d['Description'],
                "news_url": d['NewsURL'] if 'NewsURL' in d else "",
                "update_time": Time.format(d['UpdateTime']),
                "logo_url": logo_url
            }
            documents.append(document)
        
        await collection.delete_many({"area": area}) # 刪除該區域所有資料
        await collection.insert_many(documents) # 將資料存入MongoDB
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}

async def numberToText(number : int):
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
            return "通阻資訊"
        case 99:
            return "其他"
