from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

router = APIRouter(tags=["5.觀光資訊(Website)"],prefix="/Website/Information/Tourism")

@router.put("/TouristFood",summary="【Update】觀光景點-全臺觀光景點餐飲")
async def updateTouristFoodAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1. 交通部運輸資料流通服務平臺(TDX) - 取得所有觀光餐飲資料
                https://tdx.transportdata.tw/api-service/swagger/basic/cd0226cf-6292-4c35-8a0d-b595f0b15352#/Tourism/TourismApi_Restaurant_2242\n
        二、Input \n
                1. 
        三、Output \n
                1. 
        四、說明 \n
                1.
        """
        Token.verifyToken(token.credentials,"admin") # JWT驗證
        return updateTouristFood()

def updateTouristFood():
        collection = MongoDB.getCollection("traffic_hero","tourism_tourist_food")
        try:
                url = f"https://tdx.transportdata.tw/api/basic/v2/Tourism/Restaurant?%24format=JSON" # 取得資料來源網址
                data = TDX.getData(url) # 取得資料

                # 處理無圖片的資料
                for result in data:
                        if(result['Picture'].get('PictureUrl1') == None):
                                result['Picture']['PictureUrl1'] = 'https://cdn3.iconfinder.com/data/icons/basic-2-black-series/64/a-92-256.png'

                collection.drop() # 刪除該collection所有資料
                collection.insert_many(data) # 將資料存入MongoDB
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}

        return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}