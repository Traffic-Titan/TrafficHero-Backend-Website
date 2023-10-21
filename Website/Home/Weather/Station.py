from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import Service.TDX as TDX
import requests
from Main import MongoDB # 引用MongoDB連線實例
import time
from pydantic import BaseModel
from dotenv import load_dotenv
import os

router = APIRouter(tags=["1.首頁(Website)"],prefix="/Website/Home")

@router.put("/Weather/Station", summary="【Update】中央氣象署-無人氣象測站") 
async def updateStation(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1.  \n
        二、Input \n
                1. 
        三、Output \n
                1. 
        四、說明 \n
                1.
        """
        Token.verifyToken(token.credentials,"admin") # JWT驗證
        
        # 中央氣象署API Key
        load_dotenv()
        CWA_API_Key = os.getenv('CWA_API_Key') 
        
        collection = MongoDB.getCollection("traffic_hero","weather_station") # 取得無人氣象測站資料
        
        try:
                observation_station_unmanned =  requests.get(f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization={CWA_API_Key}').json()
                collection.delete_many({}) # 清空資料庫
                collection.insert_many(observation_station_unmanned['records']['location']) # 將無人氣象測站資料存入資料庫
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}
        
        return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}

@router.put("/Weather/StationList", summary="【Update】中央氣象署-無人氣象測站清單") 
async def updateStationList(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1.  \n
        二、Input \n
                1. 
        三、Output \n
                1. 
        四、說明 \n
                1.
        """
        Token.verifyToken(token.credentials,"admin") # JWT驗證
        
        # 中央氣象署API Key
        load_dotenv()
        CWA_API_Key = os.getenv('CWA_API_Key') 
        
        collection = MongoDB.getCollection("traffic_hero","weather_station_list") # 取得無人氣象測站資料
        
        try:
                observation_station_unmanned =  requests.get(f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/C-B0074-002?Authorization={CWA_API_Key}&status=%E7%8F%BE%E5%AD%98%E6%B8%AC%E7%AB%99').json()
                collection.delete_many({}) # 清空資料庫
                collection.insert_many(observation_station_unmanned['records']["data"]["stationStatus"]['station']) # 將無人氣象測站資料存入資料庫
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}
        
        return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}