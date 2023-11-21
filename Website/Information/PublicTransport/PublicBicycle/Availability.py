from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

router = APIRouter(tags=["4-2.大眾運輸資訊(Website)"],prefix="/Website/Information/PublicTransport")
collection = MongoDB.getCollection("traffic_hero","information_public_bicycle_availability")

@router.put("/PublicBicycle/Availability",summary="【Update】大眾運輸資訊-取得動態指定[縣市]的公共自行車即時車位資料")
async def updateStation(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX) - 取得動態指定[縣市]的公共自行車即時車位資料
                https://tdx.transportdata.tw/api-service/swagger/basic/2cc9b888-a592-496f-99de-9ab35b7fb70d#/Bike/BikeApi_Availability_2181 \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證

    areas = ["Taipei","NewTaipei","Taoyuan","Hsinchu","HsinchuCounty","MiaoliCounty","Taichung","Chiayi","Tainan","Kaohsiung","PingtungCounty","KinmenCounty"]
    collection.drop() # 刪除所有資料
    
    for area in areas: # 依照區域更新資料
        dataToDatabase(area)

    return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}
    
def dataToDatabase(area: str):
    try:
        url = f"https://tdx.transportdata.tw/api/basic/v2/Bike/Availability/City/{area}?%24format=JSON" # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        
        documents = []
        for d in data:
            documents.append({
                "station_uid": d["StationUID"],
                "station_id": d["StationID"],
                "service_status": idToStatus(d["ServiceStatus"]),
                "service_type": idToType(d["ServiceType"]),
                "available_rent_bikes": d["AvailableRentBikes"],
                "available_return_bikes": d["AvailableReturnBikes"],
                "available_rent_bikes_detail": {
                    "general_bikes": d["AvailableRentBikesDetail"]["GeneralBikes"],
                    "electric_bikes": d["AvailableRentBikesDetail"]["ElectricBikes"]
                },
                "src_update_time": d["SrcUpdateTime"],
                "update_time": d["UpdateTime"]
            })
        
        collection.insert_many(documents) # 將資料存入MongoDB
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}

def idToStatus(id: int):
    match id:
        case 0:
            return "停止營運"
        case 1:
            return "正常營運"
        case 2:
            return "暫停營運"

def idToType(id: int):
    match id:
        case 1:
            return "YouBike1.0"
        case 2:
            return "YouBike2.0"
        case 3:
            return "T-Bike"
        case 4:
            return "P-Bike"
        case 5:
            return "K-Bike"