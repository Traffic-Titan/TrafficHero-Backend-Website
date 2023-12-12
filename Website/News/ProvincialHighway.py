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
import Function.Time as Time
import Function.Link as Link
from Main import MongoDB # 引用MongoDB連線實例
import Function.Logo as Logo
import Function.Area as Area
from bson import ObjectId

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")

"""
資料來源:省道最新消息
https://tdx.transportdata.tw/api-service/swagger/basic/7f07d940-91a4-495d-9465-1c9df89d709c#/HighwayTraffic/Live_News_Highway
省道 起、迄點牌面資料
https://tdx.transportdata.tw/api-service/swagger/basic/30bc573f-0d73-47f2-ac3c-37c798b86d37#/Road/PhysicalNetwork_03016
省道里程坐標：https://data.gov.tw/dataset/7040
"""
def getCountry(title:str,matchName:str):
    #讀檔 省道里程座標.csv
    with open(r'./News/省道里程坐標.csv',encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                #透過正則表示法 及 比對到的省道名稱，與csv的資料比對後，回傳csv檔的縣市欄位(row[2])
                if(row[0] == matchName and re.search("\d\d\d[A-Z]|\d\d[A-Z]",title).group() in row[10]):
                    return row[2]
            except:
                pass
        return None

@router.put("/ProvincialHighway",summary="【Update】最新消息-省道")
async def updateNewsAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX) - 省道最新消息資料 v2
                https://tdx.transportdata.tw/api-service/swagger/basic/7f07d940-91a4-495d-9465-1c9df89d709c#/HighwayTraffic/Live_News_Highway \n
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
    try:
        url = Link.get("traffic_hero", "news_source", "provincial_highway", "All")
        data = TDX.getData(url)
        
        documents = []
        logo_url = Logo.get("provincial_highway", "All")
        
        collection = await MongoDB.getCollection("traffic_hero", "road_area")
        for d in data["Newses"]:
            patterns = [r"台\d", r"國\d"]
            pattern = "|".join(patterns)
            match = re.search(pattern, d['Title'])
            
            if match:
                result = collection.find_one({"RoadName": match.group()}, {"_id": 0, "CityList": 1})
                for area in result.get("CityList"):
                    document = {
                        "area": Area.chineseToEnglish(area.get("CityName")),
                        "news_id": d['NewsID'],
                        "title": d['Title'],
                        "news_category": await numberToText(d['NewsCategory']),
                        "description": d['Description'],
                        "news_url": d['NewsURL'] if 'NewsURL' in d else "",
                        "update_time": Time.format(d['UpdateTime']),
                        "logo_url": logo_url
                    }
                    documents.append(document)
                continue

            for area in Area.chinese:
                short_name = area[:2]
                if short_name in d['Title']:
                    document = {
                        "area": Area.chineseToEnglish(area),
                        "news_id": d['NewsID'],
                        "title": d['Title'],
                        "news_category": await numberToText(d['NewsCategory']),
                        "description": d['Description'],
                        "news_url": d['NewsURL'] if 'NewsURL' in d else "",
                        "update_time": Time.format(d['UpdateTime']),
                        "logo_url": logo_url
                    }
                    documents.append(document)
                    break

            else:
                document = {
                    "area": "All",
                    "news_id": d['NewsID'],
                    "title": d['Title'],
                    "news_category": await numberToText(d['NewsCategory']),
                    "description": d['Description'],
                    "news_url": d['NewsURL'] if 'NewsURL' in d else "",
                    "update_time": Time.format(d['UpdateTime']),
                    "logo_url": logo_url
                }
                documents.append(document)


        collection = await MongoDB.getCollection("traffic_hero", "news_provincial_highway")
        collection.drop()
        collection.insert_many(documents)
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}
        
    return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}


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
