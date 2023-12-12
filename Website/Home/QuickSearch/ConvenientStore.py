from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
from bson import ObjectId
import Service.TDX as TDX
import pandas as pd
from geopy.geocoders import Nominatim
import requests

router = APIRouter(tags=["1.首頁(Website)"],prefix="/Website/Home")

# 因此資料集需要額外GeoCoding，所以不會有更新Function

# @router.put("/QuickSearch/ConvenientStore",summary="【Update】快速尋找地點-便利商店列表")
# async def updateConvenientStoreListAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
#         """
#         一、資料來源: \n
#                 1. 政府資料開放平臺 - 全國5大超商資料集
#                 https://data.gov.tw/dataset/32086 \n
#         二、Input \n
#                 1. 
#         三、Output \n
#                 1. 
#         四、說明 \n
#                 1.
#         """
#         Token.verifyToken(token.credentials,"admin") # JWT驗證
#         return updateConvenientStoreList()

# def updateConvenientStoreList():
#         collection = await MongoDB.getCollection("traffic_hero","convenient_store_list_new")
#         collection_old = await MongoDB.getCollection("traffic_hero","convenient_store_list_old")
#         try:
#                 # 網路上的CSV檔URL
#                 csv_url = "https://data.gcis.nat.gov.tw/od/file?oid=C054F05C-0A6B-428C-B388-288BDB0618E4"

#                 # 從網路上讀取CSV檔
#                 df = pd.read_csv(csv_url, encoding='utf-8')

#                 # 將DataFrame轉換為字典
#                 records = df.to_dict(orient='records')

#                 documents = []
#                 count = 0
#                 for r in records:
#                         count += 1
#                         print(f"更新第{count}筆資料")

#                         if int(r["分公司狀態"]) == 1: # 核准設立
#                                 old_address = collection_old.find_one({"地址": r["分公司地址"].strip()}, {"_id": 0})
                                                                     
#                                 document = {
#                                         "company_id": int(r["公司統一編號"]),
#                                         "branch_id": int(r["分公司統一編號"]),
#                                         "company_name": r["公司名稱"].strip(),
#                                         "branch_name": r["分公司名稱"].strip(),
#                                         "branch_address": r["分公司地址"].strip(),
#                                         "status": "核准設立",
#                                         "location": {
#                                                 "longitude": longitude,
#                                                 "latitude": latitude
#                                         }
#                                 }
                                
                                 
#                                 documents.append(document)
                                                
#                 # 刪除舊的collection資料
#                 await collection.drop()

#                 # 插入新的資料
#                 await collection.insert_many(documents)
#                 return {"message": f"更新成功，總筆數:{await collection.count_documents({})}"}
#         except Exception as e:
#                 return {"message": f"更新失敗，錯誤訊息:{e}"}
