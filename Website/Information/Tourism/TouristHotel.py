from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
import Function.Weather as Weather

router = APIRouter(tags=["5.觀光資訊(Website)"],prefix="/Website/Information/Tourism")

@router.put("/TouristHotel",summary="【Update】觀光景點-全臺觀光景點飯店")
async def updateTouristHotelAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1. 交通部運輸資料流通服務平臺(TDX) - 取得所有觀光旅宿資料
                https://tdx.transportdata.tw/api-service/swagger/basic/cd0226cf-6292-4c35-8a0d-b595f0b15352#/Tourism/TourismApi_Hotel_2244 \n
        二、Input \n
                1. 
        三、Output \n
                1. 
        四、說明 \n
                1.
        """
        Token.verifyToken(token.credentials,"admin") # JWT驗證
        return await updateTouristHotel()

async def updateTouristHotel():
        collection = MongoDB.getCollection("traffic_hero","tourism_tourist_hotel")
        try:
                url = f"https://tdx.transportdata.tw/api/basic/v2/Tourism/Hotel?%24format=JSON" # 取得資料來源網址
                data = TDX.getData(url) # 取得資料

                for result in data:
                        result["Weather"] = await Weather.getWeather(result['Position']['PositionLon'],result['Position']['PositionLat'])
                        if(result['Picture'].get('PictureUrl1') == None): # 處理無圖片的資料
                                result['Picture']['PictureUrl1'] = 'https://cdn3.iconfinder.com/data/icons/basic-2-black-series/64/a-92-256.png'
                
                collection.drop() # 刪除該collection所有資料
                collection.insert_many(result) # 將資料存入MongoDB
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}

        return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}