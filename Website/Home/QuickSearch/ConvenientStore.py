from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
from bson import ObjectId
import Service.TDX as TDX
import pandas as pd

router = APIRouter(tags=["1.首頁(Website)"],prefix="/Website/Home")

@router.put("/QuickSearch/ConvenientStore",summary="【Update】快速尋找地點-便利商店列表")
async def updateConvenientStoreListAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1. 政府資料開放平臺 - 全國5大超商資料集
                https://data.gov.tw/dataset/32086 \n
        二、Input \n
                1. 
        三、Output \n
                1. 
        四、說明 \n
                1.
        """
        Token.verifyToken(token.credentials,"admin") # JWT驗證
        return updateConvenientStoreList()

def updateConvenientStoreList():
        collection = MongoDB.getCollection("traffic_hero","convenient_store_list")
        
        try:
                # 網路上的CSV檔URL
                csv_url = "https://data.gcis.nat.gov.tw/od/file?oid=C054F05C-0A6B-428C-B388-288BDB0618E4"

                # 從網路上讀取CSV檔
                df = pd.read_csv(csv_url, encoding='utf-8')

                # 將DataFrame轉換為字典
                records = df.to_dict(orient='records')

                # 刪除舊的collection資料
                collection.drop()

                # 插入新的資料
                collection.insert_many(records)
                return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}