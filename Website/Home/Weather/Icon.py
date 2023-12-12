from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import Service.TDX as TDX
import requests
from Main import MongoDB # 引用MongoDB連線實例
import time
from pydantic import BaseModel

router = APIRouter(tags=["1.首頁(Website)"],prefix="/Website/Home")

class weather_icon(BaseModel):
    id: str
    icon_url_day: str
    icon_url_night: str

@router.get("/Weather/Icon", summary="【Read】首頁-天氣狀態圖示")
async def getWeatherIcon(type1: str = "all", token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    collection = await MongoDB.getCollection("traffic_hero","weather_icon")
    
    match type1:
        case "all":
                result = collection.find({},{"_id":0})
        case "晴":
                result = collection.find({"type1": "晴"}, {"_id":0})
        case "多雲":
                result = collection.find({"type1": "多雲"}, {"_id":0})
        case "陰":
                result = collection.find({"type1": "陰"}, {"_id":0})
    
    return list(result)

@router.put("/Weather/Icon", summary="【Update】首頁-天氣狀態圖示")
async def updateWeatherIcon(data: weather_icon, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    collection = await MongoDB.getCollection("traffic_hero","weather_icon")
    
    collection.update_one({"id": data.id},{"$set":{ "icon_url_day": data.icon_url_day,"icon_url_night": data.icon_url_night}})
    
    return {"message":"更新成功"}
    
# @router.delete("/Weather/Icon", summary="【Delete】首頁-天氣狀態圖示")
# async def deleteWeatherIcon(data: weather_icon, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
#     """
#     一、資料來源: \n
#             1. 
#     二、Input \n
#             1. 
#     三、Output \n
#             1. 
#     四、說明 \n
#             1.
#     """
#     Token.verifyToken(token.credentials,"admin") # JWT驗證
    
#     collection.delete_one({"type": data.type, "weather": data.weather})
    
#     return {"message":"刪除成功"}

# @router.post("/Weather/Icon", summary="【Create】首頁-天氣狀態圖示")
# async def createWeatherIcon(data: weather_icon, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
#     """
#     一、資料來源: \n
#             1. 
#     二、Input \n
#             1. 
#     三、Output \n
#             1. 
#     四、說明 \n
#             1.
#     """
#     Token.verifyToken(token.credentials,"admin") # JWT驗證
    
#     if collection.find_one({"type": data.type, "weather": data.weather}) != None:
#         return {"message":f"新增失敗，已有此類別與天氣狀態 ({data.type}-{data.weather})"}
#     else:
#         collection.insert_one(data.dict())
    
#     return {"message":"新增成功"}