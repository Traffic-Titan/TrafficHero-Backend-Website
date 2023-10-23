from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from shapely.geometry import Point
from pymongo import GEO2D
from bson.son import SON
from pymongo import GEOSPHERE

router = APIRouter(tags=["1.首頁(Website)"],prefix="/Website/Home")

@router.put("/RoadCondition",summary="【Update】附近路況")
async def updateRoadConditionAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
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
        return updateRoadCondition()

def updateRoadCondition():
        collection = MongoDB.getCollection("traffic_hero","road_condition_freeway")
        try:
                documents = []
                
                collection = MongoDB.getCollection("traffic_hero","road_condition_provincial_highway")
                documents.extend(collection.find({},{"_id":0}))
                
                collection = MongoDB.getCollection("traffic_hero","road_condition_freeway")
                documents.extend(collection.find({},{"_id":0}))

                collection = MongoDB.getCollection("traffic_hero","road_condition")
                collection.drop() # 刪除該collection所有資料
                collection.insert_many(documents) # 將資料存入MongoDB
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}

        return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}
