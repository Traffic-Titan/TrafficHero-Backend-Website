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
        return await updateRoadCondition()

async def updateRoadCondition():
    try:
        documents = []

        collection_provincial_highway = await MongoDB.getCollection("traffic_hero", "road_condition_provincial_highway")
        async for doc in collection_provincial_highway.find({}, {"_id": 0}):
            documents.append(doc)

        collection_freeway = await MongoDB.getCollection("traffic_hero", "road_condition_freeway")
        async for doc in collection_freeway.find({}, {"_id": 0}):
            documents.append(doc)

        collection_local_road = await MongoDB.getCollection("traffic_hero", "road_condition_local_road")
        async for doc in collection_local_road.find({}, {"_id": 0}):
            documents.append(doc)

        collection_road_condition = await MongoDB.getCollection("traffic_hero", "road_condition")
        await collection_road_condition.drop() # 刪除該 collection 所有資料
        if documents:
            await collection_road_condition.insert_many(documents) # 將資料存入 MongoDB
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}

    return {"message": f"更新成功，總筆數:{await collection_road_condition.count_documents({})}"}

