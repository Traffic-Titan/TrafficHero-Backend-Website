from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

router = APIRouter(tags=["4-2.大眾運輸資訊(Website)"],prefix="/Website/Information/PublicTransport")

@router.put("/InterCityBusRoute",summary="【Update】大眾運輸資訊-全台客運公車路線")
async def updateBusRoute(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1. https://tdx.transportdata.tw/api-service/swagger/basic/2998e851-81d0-40f5-b26d-77e2f5ac4118#/InterCityBus/InterCityBusApi_StopOfRoute_2068  \n
        二、Input \n
                1. 
        三、Output \n
                1. 
        四、說明 \n
                1.
        """
        Token.verifyToken(token.credentials,"admin") # JWT驗證

        collection = await MongoDB.getCollection("traffic_hero","information_interCity_bus_route")
        collection.drop() # 刪除該collection所有資料

        await dataToDatabase()

        return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}

async def dataToDatabase():
        collection = await MongoDB.getCollection("traffic_hero","information_interCity_bus_route")
        try:
                url = f"https://tdx.transportdata.tw/api/basic/v2/Bus/StopOfRoute/InterCity?%24format=JSON" # 取得資料來源網址
                data = TDX.getData(url) # 取得資料
                collection.insert_many(data) # 將資料存入MongoDB
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}