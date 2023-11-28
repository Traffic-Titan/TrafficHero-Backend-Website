from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
import Service.TDX as TDX
import requests
import xml.etree.ElementTree as ET
from Main import MongoDB # 引用MongoDB連線實例
import time
import Function.Logo as Logo

router = APIRouter(tags=["1.首頁(Website)"],prefix="/Website/Home")
collection = MongoDB.getCollection("traffic_hero","operational_status")

@router.put("/OperationalStatus", summary="【Update】大眾運輸-營運狀況") # 先初步以北中南東離島分類，以後再依照縣市分類
async def updateAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 交通部運輸資料流通服務平臺(TDX)
                資料類型: 營運通阻
                https://tdx.transportdata.tw/data-service/basic/ \n
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
    # 城際
    await TRA()
    await THSR()
    await InterCityBus()
    
    # 捷運
    await MRT("TRTC")
    await MRT("TYMC")
    await MRT("KRTC")
    await MRT("TMRT")
    await MRT("TRTCMG") # 貓空纜車
    
    # 公車
    # 北部
    await Bus_v2("Taipei")
    await Bus_v2("NewTaipei")
    await Bus_v2("Keelung")
    await Bus_v2("Taoyuan")
    await Bus_v2("Hsinchu")
    await Bus_v2("HsinchuCounty")
    await Bus_v2("YilanCounty")
    
    # 中部
    await Bus_v2("MiaoliCounty")
    await Bus_v2("Taichung")
    await Bus_v2("ChanghuaCounty")
    await Bus_v2("YunlinCounty")
    
    # 南部            
    await Bus_v2("Chiayi"),
    await Bus_v2("ChiayiCounty")
    await Bus_v3("Tainan")
    await Bus_v2("Kaohsiung")
    await Bus_v2("PingtungCounty")

    # 東部
    await Bus_v2("TaitungCounty")
    await Bus_v2("HualienCounty")
    
    # 離島      
    await Bus_v2("PenghuCounty")
    
    return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}

async def dataToDatabase(name: str, status:str, logo_url: str):
    try:
        document = {
            "name": name,
            "status": status,
            "status_text": "停止營運" if status == "red" else "部分營運" if status == "yellow" else "正常營運",
            "logo_url": logo_url
        }

        collection.delete_many({"name": name}) # 刪除該類別的所有資料
        collection.insert_one(document) # 將資料存入MongoDB
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}

async def TRA(): # 臺鐵
    url = "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/Alert?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設
    
    try:
        data = TDX.getData(url) # 取得資料
        
        for alert in data["Alerts"]:        
            if  alert["Status"] == 0:
                status = "red"  # 停止營運
            elif  alert["Status"] == 2 and status != "red":
                status = "yellow"  # 部分營運
            elif  alert["Status"] == 1 and status not in ["red", "yellow"]:
                status = "green"  # 正常營運
    except Exception as e:
        print(e)
            
    await dataToDatabase("臺鐵", status, Logo.get("taiwan_railway", "All"))

async def THSR(): # 高鐵
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/THSR/AlertInfo?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設
    
    try:
        data = TDX.getData(url) # 取得資料
        
        match data[0]["Status"]:
            case "":
                status = "green"  # 正常營運
            case "▲":
                status = "yellow"  # 部分營運
            case "X":
                status = "red"  # 停止營運
    except Exception as e:
        print(e)
            
    await dataToDatabase("高鐵", status, Logo.get("taiwan_high_speed_rail", "All"))

async def MRT(system: str): # 捷運
    url = f"https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/Alert/{system}?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設
    
    try:
        data = TDX.getData(url) # 取得資料
        
        for alert in data["Alerts"]:        
            if  alert["Status"] == 0:
                status = "red"  # 停止營運
            elif  alert["Status"] == 2 and status != "red":
                status = "yellow"  # 部分營運
            elif  alert["Status"] == 1 and status not in ["red", "yellow"]:
                status = "green"  # 正常營運
    except Exception as e:
        print(e)
    
    match system:
        case "TRTC":
            await dataToDatabase("臺北捷運", status, Logo.get("mrt", "TaipeiCity"))
        case "TYMC":
            await dataToDatabase("桃園捷運", status, Logo.get("mrt", "TaoyuanCity"))
        case "KRTC":
            await dataToDatabase("高雄捷運", status, Logo.get("mrt", "KaohsiungCity"))
        case "TRTCMG":
            await dataToDatabase("貓空纜車", status, Logo.get("mrt", "TaipeiCity"))
        case "TMRT":
            await dataToDatabase("臺中捷運", status, Logo.get("mrt", "TaichungCity"))

async def InterCityBus(): # 公路客運
    url = "https://tdx.transportdata.tw/api/basic/v2/Bus/Alert/InterCity?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設
    
    try:
        data = TDX.getData(url) # 取得資料
        
        if data[0]["Status"] == 0:
            status = "red"  # 停止營運
        elif data[0]["Status"] == 2 and status != "red":
            status = "yellow"  # 部分營運
        elif data[0]["Status"] == 1 and status not in ["red", "yellow"]:
            status = "green"  # 正常營運
    except Exception as e:
        print(e)
        
    await dataToDatabase("公路客運", status, Logo.get("intercity_bus", "All"))

async def Bus_v2(area: str): # 各縣市公車
    url = f"https://tdx.transportdata.tw/api/basic/v2/Bus/Alert/City/{area}?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設

    try:
        data = TDX.getData(url) # 取得資料

        if data[0]["Status"] == 0:
            status = "red"  # 停止營運
        elif data[0]["Status"] == 2 and status != "red":
            status = "yellow"  # 部分營運
        elif data[0]["Status"] == 1 and status not in ["red", "yellow"]:
            status = "green"  # 正常營運
    except Exception as e:
        print(e)
        
    match area:
        case "Keelung":
            await dataToDatabase("基隆市公車", status, Logo.get("bus", "KeelungCity"))
        case "Taipei":
            await dataToDatabase("臺北市公車", status, Logo.get("bus", "TaipeiCity"))
        case "NewTaipei":
            await dataToDatabase("新北市公車", status, Logo.get("bus", "NewTaipeiCity"))
        case "Taoyuan":
            await dataToDatabase("桃園市公車", status, Logo.get("bus", "TaoyuanCity"))
        case "Hsinchu":
            await dataToDatabase("新竹市公車", status, Logo.get("bus", "HsinchuCity"))
        case "HsinchuCounty":
            await dataToDatabase("新竹縣公車", status, Logo.get("bus", "HsinchuCounty"))
        case "MiaoliCounty":
            await dataToDatabase("苗栗縣公車", status, Logo.get("bus", "MiaoliCounty"))
        case "Taichung":
            await dataToDatabase("臺中市公車", status, Logo.get("bus", "TaichungCity"))
        case "ChanghuaCounty":
            await dataToDatabase("彰化縣公車", status, Logo.get("bus", "ChanghuaCounty"))
        case "YunlinCounty":
            await dataToDatabase("雲林縣公車", status, Logo.get("bus", "YunlinCounty"))
        case "Chiayi":
            await dataToDatabase("嘉義市公車", status, Logo.get("bus", "ChiayiCity"))
        case "ChiayiCounty":
            await dataToDatabase("嘉義縣公車", status, Logo.get("bus", "ChiayiCounty"))
        case "Tainan": # Bus_v3
            pass
        case "Kaohsiung":
            await dataToDatabase("高雄市公車", status ,Logo.get("bus", "KaohsiungCity"))
        case "PingtungCounty":
            await dataToDatabase("屏東縣公車", status ,Logo.get("bus", "PingtungCounty"))
        case "TaitungCounty":
            await dataToDatabase("臺東縣公車", status ,Logo.get("bus", "TaitungCounty"))
        case "HualienCounty":
            await dataToDatabase("花蓮縣公車", status ,Logo.get("bus", "HualienCounty"))
        case "YilanCounty":
            await dataToDatabase("宜蘭縣公車", status ,Logo.get("bus", "YilanCounty"))
        case "PenghuCounty":
            await dataToDatabase("澎湖縣公車", status, Logo.get("bus", "PenghuCounty"))

async def Bus_v3(area: str): # 各縣市公車
    url = f"https://tdx.transportdata.tw/api/basic/v3/Bus/Alert/City/{area}?%24format=JSON" # 先寫死，以後會再放到資料庫
    status = "無資料" # 預設

    try:
        data = TDX.getData(url) # 取得資料
        
        count = len(data["Alerts"])
        # status = "red"  # 停止營運(資料無法判斷)
        if count != 0 and status != "red":
            status = "yellow"  # 部分營運
        elif count == 0 and status not in ["red", "yellow"]:
            status = "green"  # 正常營運
    except Exception as e:
        print(e)
        
    match area:
        case "Tainan":
            await dataToDatabase("臺南市公車", status, Logo.get("bus", "TainanCity"))