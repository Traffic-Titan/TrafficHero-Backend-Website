from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

router = APIRouter(tags=["5.觀光資訊(Website)"],prefix="/Website/Information")

@router.put("/Tourism/Parking",summary="【Update】觀光景點-全臺觀光景點停車場資料")
async def updateAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1. 交通部運輸資料流通服務平臺(TDX) - 取得所有觀光景點之停車場資料
                https://tdx.transportdata.tw/api-service/swagger/basic/945f57da-f29d-4dfd-94ec-c35d9f62be7d#/TourismCarPark/ParkingApi_TourismCarPark \n
        二、Input \n
                1. 
        三、Output \n
                1. 
        四、說明 \n
                1.
        """
        Token.verifyToken(token.credentials,"admin") # JWT驗證
        return await update()

async def update():
        collection = MongoDB.getCollection("traffic_hero","tourism_parkinglot")
        try:
                url = f"https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/CarPark/Tourism?%24format=JSON" # 取得資料來源網址
                data = TDX.getData(url) # 取得資料
                
                collection.drop() # 刪除該collection所有資料
                collection.insert_many(data['CarParks']) # 將資料存入MongoDB
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}

        return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}