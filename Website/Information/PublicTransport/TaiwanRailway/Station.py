from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

router = APIRouter(tags=["4-2.大眾運輸資訊(Website)"],prefix="/Website/Information/PublicTransport/TaiwanRailway")

@router.put("/Station",summary="【Update】大眾運輸資訊-臺鐵車站基本資料")
async def update(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
         1.  交通部運輸資料流通服務平臺(TDX) - 臺鐵車站基本資料
        https://tdx.transportdata.tw/api-service/swagger/basic/5fa88b0c-120b-43f1-b188-c379ddb2593d#/TRA/StationApiController_Get_3201 \n
    二、Input \n
        1. 
    三、Output \n
        1. 
    四、說明 \n
        1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證

    collection = await MongoDB.getCollection("traffic_hero","information_taiwan_railway_station")
    
    try:
        url = f"https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/Station?%24format=JSON" # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        
        stations = data.get("Stations", [])
        
        await collection.drop() # 刪除該collection所有資料
        await collection.insert_many(stations) # 將資料存入MongoDB
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}

    return {"message": f"更新成功，總筆數:{await collection.count_documents({})}"}
    