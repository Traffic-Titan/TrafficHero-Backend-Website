from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

router = APIRouter(tags=["5.觀光資訊(Website)"],prefix="/Website/Information/Tourism")
collection = MongoDB.getCollection("traffic_hero","tourism_tourist_activity")
@router.put("/TouristActivity",summary="【Update】觀光景點-全臺觀光景點活動")
async def TouristActivity(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. https://tdx.transportdata.tw/api-service/swagger/basic/cd0226cf-6292-4c35-8a0d-b595f0b15352#/Tourism/TourismApi_Activity_2246 \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection.drop() # 刪除該collection所有資料
    
    dataToDatabase()

    return f"已更新筆數:{collection.count_documents({})}"

def dataToDatabase():
    try:
        url = f"https://tdx.transportdata.tw/api/basic/v2/Tourism/Activity?%24format=JSON" # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        collection.insert_many(data) # 將資料存入MongoDB
    except Exception as e:
        print(e)