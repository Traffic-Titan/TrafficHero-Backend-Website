from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

router = APIRouter(tags=["4-2.大眾運輸資訊(Website)"],prefix="/Website/Information/PublicTransport/Bus")

@router.put("/StopOfRoute",summary="【Update】大眾運輸資訊-市區公車之路線站序資料")
async def update(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX) - 取得指定[縣市]的市區公車路線站序資料
            https://tdx.transportdata.tw/api-service/swagger/basic/2998e851-81d0-40f5-b26d-77e2f5ac4118#/CityBus/CityBusApi_StopOfRoute_2039 \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證

    collection = await MongoDB.getCollection("traffic_hero","information_bus_stop_of_route")
    
    areas = ["Taipei","NewTaipei","Taoyuan","Taichung","Hsinchu","HsinchuCounty","MiaoliCounty","Taichung","Chiayi",'ChiayiCounty',"Tainan","Kaohsiung","PingtungCounty","KinmenCounty",'Keelung','YilanCounty','ChanghuaCounty','NantouCounty','YunlinCounty','HuanlienCounty','TaitungCounty','PenghuCounty','LienchiangCounty']

    for area in areas: # 依照區域更新資料
        await dataToDatabase(area)

    return {"message": f"更新成功，總筆數:{await collection.count_documents({})}"}
    
async def dataToDatabase(area: str):
    collection = await MongoDB.getCollection("traffic_hero","information_bus_stop_of_route")
    try:
        url = f"https://tdx.transportdata.tw/api/basic/v2/Bus/StopOfRoute/City/{area}?%24format=JSON" # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        
        await collection.delete_many({"area": area}) # 刪除該區域所有資料
        await collection.insert_many(data) # 將資料存入MongoDB
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}