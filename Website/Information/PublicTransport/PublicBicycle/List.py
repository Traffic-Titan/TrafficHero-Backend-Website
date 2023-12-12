from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX

router = APIRouter(tags=["4-2.大眾運輸資訊(Website)"],prefix="/Website/Information/PublicTransport")

@router.put("/PublicBicycle/List",summary="【Update】大眾運輸資訊-公共自行車租借站位資料")
async def updateStation(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX) - 取得指定[縣市]的公共自行車租借站位資料
                https://tdx.transportdata.tw/api-service/swagger/basic/2cc9b888-a592-496f-99de-9ab35b7fb70d#/Bike/BikeApi_Station_2180 \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證

    collection = await MongoDB.getCollection("traffic_hero","information_public_bicycle_list")
    
    areas = ["Taipei","NewTaipei","Taoyuan","Hsinchu","HsinchuCounty","MiaoliCounty","Taichung","Chiayi","Tainan","Kaohsiung","PingtungCounty","KinmenCounty"]
    collection.drop() # 刪除所有資料
    
    for area in areas: # 依照區域更新資料
        await dataToDatabase(area)

    return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}
    
async def dataToDatabase(area: str):
    collection = await MongoDB.getCollection("traffic_hero","information_public_bicycle_list")
    
    try:
        url = f"https://tdx.transportdata.tw/api/basic/v2/Bike/Station/City/{area}?%24format=JSON" # 取得資料來源網址
        data = TDX.getData(url) # 取得資料
        
        documents = []
        for d in data:
            documents.append({
                "area": idToArea(d["AuthorityID"]),
                "station_uid": d["StationUID"],
                "station_id": d["StationID"],
                "station_name_zh_tw": convert(d["StationName"]["Zh_tw"]),
                # "station_name_en": d["StationName"]["En"],
                "station_address_zh_tw": d["StationAddress"]["Zh_tw"],
                # "station_address_en": d["StationAddress"]["En"],
                "bikes_capacity": d["BikesCapacity"],
                "service_type": idToType(d["ServiceType"]),
                "icon_url": typeToIconURL(idToType(d["ServiceType"])),
                "location":{
                    "longitude": d["StationPosition"]["PositionLon"],
                    "latitude": d["StationPosition"]["PositionLat"],
                },
                # "src_update_time": d["SrcUpdateTime"],
                # "update_time": d["UpdateTime"]
            })
        
        collection.insert_many(documents) # 將資料存入MongoDB
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}

def idToArea(id: str):
    match id:
        case "TXG":
            return "TaichungCity"
        case "HSZ":
            return "HsinchuCity"
        case "MIA":
            return "MiaoliCounty"
        case "NWT":
            return "NewTaipeiCity"
        case "PIF":
            return "PingtungCounty"
        case "KIN":
            return "KinmenCounty"
        case "TAO":
            return "TaoyuanCity"
        case "TPE":
            return "TaipeiCity"
        case "KHH":
            return "KaohsiungCity"
        case "TNN":
            return "TainanCity"
        case "CYI":
            return "ChiayiCity"
        case "HSQ":
            return "HsinchuCounty"
        
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
        
def convert(station_name: str):
    # YouBike2.0_綠川東中山路口 轉換成 綠川東中山路口
    return station_name.split("YouBike2.0_")[1]

def typeToIconURL(type: str):
    match type:
        case "YouBike1.0":
            return "https://play-lh.googleusercontent.com/0Oku5KR_fsGnBMUi-tpQzQG5349q1jWk1N8X3d6qJaW_Bt1TVduDjeZX4daEDnXfsZM=w240-h480-rw"
        case "YouBike2.0":
            return "https://play-lh.googleusercontent.com/DmDUCLudSKb5hZV5P_i3S-oZkF-udIPfW1OSa-fq2FS9rTV5A2v_tTGgpS0wuSs0bA=w240-h480-rw"
        case "T-Bike": # 已停止服務
            return "https://cdn3.iconfinder.com/data/icons/basic-2-black-series/64/a-92-256.png"
        case "P-Bike": # 已停止服務
            return "https://cdn3.iconfinder.com/data/icons/basic-2-black-series/64/a-92-256.png"
        case "K-Bike":
            return "https://play-lh.googleusercontent.com/LlLuP2QHI7UfmqVeidItAdwQ1BXa4aobBrPQWQEzjwEOFudZ-pErViPFloT4JWkJ_7Uy=w240-h480-rw"