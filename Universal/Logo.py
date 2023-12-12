"""
暫緩處理
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例

router = APIRouter(tags=["通用功能"],prefix="/Universal/Logo")

@router.get("/Get",summary="【Read】(Dev)")
async def get(Type: str, Area: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = await MongoDB.getCollection("Logo",Type)
    result =  await collection.find_one({"Area": Area})
    return result["Logo"]

@router.get("/MRT",summary="【Read】取得各捷運Logo, 臺北捷運: TRTC, 桃園捷運: TYMC, 高雄捷運: KRTC, 高雄輕軌: KLRT(Dev)")
async def getMRTLogo(Region: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = await MongoDB.getCollection("2_Universal","Logo")
    
    match Region:
        case "TRTC":
            data =  await collection.find_one({"Region_EN": "TRTC"})
            return data["Logo"]
        case "TYMC":
            data =  await collection.find_one({"Region_EN": "TYMC"})
            return data["Logo"]
        case "KRTC":
            data =  await collection.find_one({"Region_EN": "KRTC"})
            return data["Logo"]
        case "KLRT":
            data =  await collection.find_one({"Region_EN": "KLRT"})
            return data["Logo"]
        case _:
            return "No Data"

@router.post("/MRT",summary="【Create】新增各捷運Logo, 臺北捷運: TRTC, 桃園捷運: TYMC, 高雄捷運: KRTC, 高雄輕軌: KLRT(Dev)")
async def setMRTLogo(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    collection = await MongoDB.getCollection("2_Universal","Logo")
    

@router.put("/MRT",summary="【Update】修改各捷運Logo, 臺北捷運: TRTC, 桃園捷運: TYMC, 高雄捷運: KRTC, 高雄輕軌: KLRT(Dev)")
async def setMRTLogo(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = await MongoDB.getCollection("2_Universal","Logo")
    await collection.drop()

    return "Success"
