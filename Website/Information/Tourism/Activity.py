from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
import Function.Weather as Weather

router = APIRouter(tags=["5.觀光資訊(Website)"],prefix="/Website/Information")

@router.put("/Tourism/Activity",summary="【Update】觀光景點-全臺觀光景點活動")
async def updateAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1. 交通部運輸資料流通服務平臺(TDX) - 取得所有觀光活動資料
                https://tdx.transportdata.tw/api-service/swagger/basic/cd0226cf-6292-4c35-8a0d-b595f0b15352#/Tourism/TourismApi_Activity_2246 \n
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
    collection = MongoDB.getCollection("traffic_hero","tourism_activity")
    
    try:
        url = f"https://tdx.transportdata.tw/api/basic/v2/Tourism/Activity?%24format=JSON" # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        
        documents = []
        for d in data:
                d["Weather"] = await Weather.getWeather(d['Position']['PositionLon'],d['Position']['PositionLat'])
                if(d['Picture'].get('PictureUrl1') == None): # 處理無圖片的資料
                     d['Picture']['PictureUrl1'] = 'https://cdn3.iconfinder.com/data/icons/basic-2-black-series/64/a-92-256.png'
                documents.append(d)
        
        collection.drop() # 刪除該collection所有資料
        collection.insert_many(documents) # 將資料存入MongoDB
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}

    return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}
