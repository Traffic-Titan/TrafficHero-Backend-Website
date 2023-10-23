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

@router.put("/RoadCondition/ProvincialHighway",summary="【Update】附近路況-省道車輛偵測器資料")
async def updateRoadCondition_ProvincialHighwayAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1. 交通部運輸資料流通服務平臺(TDX) - 省道車輛偵測器即時路況資料 v2
                https://tdx.transportdata.tw/api-service/swagger/basic/7f07d940-91a4-495d-9465-1c9df89d709c#/HighwayTraffic/Live_VD_Highway \n
        二、Input \n
                1. 
        三、Output \n
                1. 
        四、說明 \n
                1.
        """
        Token.verifyToken(token.credentials,"admin") # JWT驗證
        return updateRoadCondition_ProvincialHighway()

def updateRoadCondition_ProvincialHighway():
        collection = MongoDB.getCollection("traffic_hero","road_condition_provincial_highway")
        try:
                url = f"https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/VD/Highway?%24format=JSON" # 取得資料來源網址
                data = TDX.getData(url) # 取得資料
                
                collection.drop() # 刪除該collection所有資料
                collection.insert_many(data.get("VDLives")) # 將資料存入MongoDB
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}

        return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}

@router.put("/RoadCondition/ProvincialHighwayList",summary="【Update】附近路況-省道車輛偵測器列表")
async def updateRoadCondition_ProvincialHighwayListAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1. 交通部運輸資料流通服務平臺(TDX) - 省道車輛偵測器資料 v2
                https://tdx.transportdata.tw/api-service/swagger/basic/7f07d940-91a4-495d-9465-1c9df89d709c#/HighwayTraffic/VD_Highway \n
        二、Input \n
                1. 
        三、Output \n
                1. 
        四、說明 \n
                1.
        """
        Token.verifyToken(token.credentials,"admin") # JWT驗證
        return updateRoadCondition_ProvincialHighwayList()

def updateRoadCondition_ProvincialHighwayList():
        collection = MongoDB.getCollection("traffic_hero","road_condition_provincial_highway_list")
        try:
                url = f"https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/VD/Highway?%24format=JSON" # 取得資料來源網址
                data = TDX.getData(url) # 取得資料
                
                documents = []
                for d in data.get("VDs"):
                        documents.append({
                                "VDID": d["VDID"],
                                "SubAuthorityCode": d["SubAuthorityCode"],
                                "BiDirectional": d["BiDirectional"],
                                "DetectionLinks": d["DetectionLinks"],
                                "VDType": d["VDType"],
                                "LocationType": d["LocationType"],
                                "DetectionType": d["DetectionType"],
                                "Position": {
                                        "PositionLon": d["PositionLon"],
                                        "PositionLat": d["PositionLat"]
                                },
                                "Road": {
                                        "RoadID": d["RoadID"],
                                        "RoadName": d["RoadName"],
                                        "RoadClass": d["RoadClass"]
                                }
                        })
                
                collection.drop() # 刪除該collection所有資料
                collection.insert_many(documents) # 將資料存入MongoDB
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}

        return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}

@router.put("/RoadCondition/test",summary="【Update】附近路況-test(Dev)")
async def test(latitude: str, longitude: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        Token.verifyToken(token.credentials, "admin")  # JWT验证

        collection = MongoDB.getCollection("traffic_hero", "road_condition_provincial_highway_list")

        pipeline = [
        {
                '$addFields': {
                'distance': {
                        '$sqrt': {
                        '$add': [
                                {'$pow': [{'$subtract': ['$Position.PositionLon', float(longitude)]}, 2]},
                                {'$pow': [{'$subtract': ['$Position.PositionLat', float(latitude)]}, 2]}
                        ]
                        }
                }
                }
        },
        {
                '$sort': {'distance': 1}
        },
        {
                '$limit': 1
        },
        {
        '$project': {
            '_id': 0
        }
        }
        ]

        nearest_data = collection.aggregate(pipeline)
        
        return list(nearest_data)