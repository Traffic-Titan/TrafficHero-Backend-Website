from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from shapely.geometry import Point
from pymongo import GEO2D
from bson.son import SON
from pymongo import GEOSPHERE
import re

router = APIRouter(tags=["1.首頁(Website)"],prefix="/Website/Home")

@router.put("/RoadCondition/LocalRoad/CMS/List",summary="【Update】附近路況-地區道路CMS設備資料")
async def updateRoadCondition_LocalRoad_CMS_ListAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1. 交通部運輸資料流通服務平臺(TDX) - 取得指定[縣市]資訊可變標誌
                https://tdx.transportdata.tw/api-service/swagger/basic/7f07d940-91a4-495d-9465-1c9df89d709c#/CityTraffic/CMS_City \n
        二、Input \n
                1. 
        三、Output \n
                1. 
        四、說明 \n
                1.
        """
        Token.verifyToken(token.credentials,"admin") # JWT驗證
        return await updateRoadCondition_LocalRoad_CMS_List()

async def updateRoadCondition_LocalRoad_CMS_List():
        collection = MongoDB.getCollection("traffic_hero","road_condition_local_road_cms_list")
        try:
                areas = ["Taipei","NewTaipei","Taoyuan","Taichung","Hsinchu","HsinchuCounty","MiaoliCounty","Taichung","Chiayi",'ChiayiCounty',"Tainan","Kaohsiung","PingtungCounty",'YilanCounty','ChanghuaCounty','NantouCounty','YunlinCounty','TaitungCounty']
                documents = []
                for area in areas:
                        url = f"https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CMS/City/{area}?%24format=JSON" # 取得資料來源網址
                        data = TDX.getData(url) # 取得資料
                        documents.extend(data.get("CMSs"))
                
                collection.drop() # 刪除該collection所有資料
                collection.insert_many(documents) # 將資料存入MongoDB
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}

        return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}

@router.put("/RoadCondition/LocalRoad/CMS/Content",summary="【Update】附近路況-地區道路CMS顯示內容")
async def updateRoadCondition_LocalRoad_CMS_ContentAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1. 交通部運輸資料流通服務平臺(TDX) - 取得指定[縣市]資訊可變標誌即時資訊
                https://tdx.transportdata.tw/api-service/swagger/basic/7f07d940-91a4-495d-9465-1c9df89d709c#/CityTraffic/Live_CMS_City \n
        二、Input \n
                1. 
        三、Output \n
                1. 
        四、說明 \n
                1.
        """
        Token.verifyToken(token.credentials,"admin") # JWT驗證
        return await updateRoadCondition_LocalRoad_CMS_Content()

async def updateRoadCondition_LocalRoad_CMS_Content():
        collection = MongoDB.getCollection("traffic_hero","road_condition_local_road_cms_content")
        try:
                documents = []
                
                areas = ["Taipei","NewTaipei","Taoyuan","Taichung","Hsinchu","HsinchuCounty","MiaoliCounty","Taichung","Chiayi",'ChiayiCounty',"Tainan","Kaohsiung","PingtungCounty",'YilanCounty','ChanghuaCounty','NantouCounty','YunlinCounty','TaitungCounty']
                for area in areas:
                        url = f"https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/CMS/City/{area}?%24format=JSON" # 取得資料來源網址
                        data = TDX.getData(url) # 取得資料
                        for d in data.get("CMSLives"):
                                if d.get("MessageStatus") == 1:
                                        cms_id = d.get("CMSID")
                                        messages = [await process(message["Text"]) for message in d["Messages"] if "text" in message and message["Text"] != ""]
                                        documents.append({
                                                "CMSID": cms_id,
                                                "Messages": messages
                                        })
                
                collection.drop() # 刪除該collection所有資料
                collection.insert_many(documents) # 將資料存入MongoDB
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}

        return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}

async def process(message: str): # 將(圖)前面的字串刪除
        result = re.sub(r'.*\(圖\)', '', message)
        return result

@router.put("/RoadCondition/LocalRoad",summary="【Update】附近路況-地區道路")
async def updateRoadCondition_LocalRoadAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1. \n
        二、Input \n
                1. 
        三、Output \n
                1. 
        四、說明 \n
                1.
        """
        Token.verifyToken(token.credentials,"admin") # JWT驗證
        return await updateRoadCondition_LocalRoad()

async def updateRoadCondition_LocalRoad():
    collection = MongoDB.getCollection("traffic_hero", "road_condition_local_road")
    collection_cms_list = MongoDB.getCollection("traffic_hero", "road_condition_local_road_cms_list")
    collection_cms_content = MongoDB.getCollection("traffic_hero", "road_condition_local_road_cms_content")
    
    try:
        data = collection_cms_list.find({}, {"_id": 0})
        documents = []

        for d in data:
            cms_content = collection_cms_content.find_one({"CMSID": d.get("CMSID")}, {"_id": 0, "Messages": 1})
            
            if cms_content:
                documents.append({
                    "cms_id": d.get("CMSID"),
                    "position": {
                        "longitude": d.get("PositionLon"),
                        "latitude": d.get("PositionLat")
                        },
                    "road_name": d.get("RoadName"),
                    "content": cms_content.get("Messages")
                })

        collection.drop()
        collection.insert_many(documents)
        
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}

    return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}
