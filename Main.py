from fastapi import FastAPI, Request
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from api_analytics.fastapi import Analytics
from Service.Database import MongoDBSingleton
import Function.Time as Time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

# ---------------------------------------------------------------

async def getExecutionTime(request: Request, call_next): # 計算執行時間
    start = Time.getCurrentTimestamp() # 開始時間
    response = await call_next(request) # 等待執行
    end = Time.getCurrentTimestamp() # 結束時間

    print(f"執行時間: {end - start:.4f} 秒") # 輸出執行時間
    return response # 回傳結果

# ---------------------------------------------------------------

app = FastAPI() # 建立FastAPI物件
app.add_middleware(Analytics, api_key="a2999611-b29a-4ade-a55b-2147b706da6e")  # Add middleware(Dev)
app.middleware("http")(getExecutionTime) # 讓所有路由都可以計算執行時間

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://traffic-hero.eddie.tw/", "http://localhost:5173/"], # 安全性問題需處理
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MongoDB = MongoDBSingleton()
# scheduler = BackgroundScheduler() # 排程器
scheduler = AsyncIOScheduler()
# ---------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    load_dotenv() # 讀取環境變數
    scheduler.start() # 啟動排程
    # get_ConvenientStore()
    # SpeedLimit()
    # FreeWayTunnel()
    # getHardShoulder()
    # Scheduler.start() 
    # setInterval(Speed_Enforcement.getData())
    # setInterval(Technical_Enforcement.getData())
    # setInterval(PBS.getData())
    # Speed_Enforcement.getData()
    # Technical_Enforcement.getData()
    # PBS.getData()
    # PBS.getTaipeiRoadCondition()

@app.on_event("shutdown")
async def shutdown_event():
    # 在應用程式關閉時斷開連線
    # email_server.quit()
    MongoDB.closeConnection()

# ---------------------------------------------------------------

# 自動導向Swagger
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# ---------------------------------------------------------------

# 外部服務(Dev Only)
from Service import Email, GoogleMaps, TDX, Token
app.include_router(Email.router)
app.include_router(GoogleMaps.router)
app.include_router(TDX.router)
app.include_router(Token.router)

# ---------------------------------------------------------------

# 0.會員管理(Website)
from Website.Account import Login, Register, SSO, Code, Password, Profile
app.include_router(Login.router)
app.include_router(Register.router)
app.include_router(SSO.router)
app.include_router(Password.router)
app.include_router(Code.router)
app.include_router(Profile.router)

# 0.群組通訊(Website)
from Website.Chat import Main
app.include_router(Main.router)

# 1.首頁(Website)
from Website.Home import OperationalStatus, ParkingFee
app.include_router(OperationalStatus.router)

# 排程更新 - 大眾運輸 - 營運狀況
global count_updateOperationalStatus
count_updateOperationalStatus = 0

async def updateOperationalStatus():
    global count_updateOperationalStatus
    count_updateOperationalStatus += 1
    
    print(f"S: 更新大眾運輸 - 營運狀態 - 第{count_updateOperationalStatus}次 - {Time.format(str(Time.getCurrentDatetime()))}")
    
    await OperationalStatus.update()
    
    print(f"E: 更新大眾運輸 - 營運狀態 - 第{count_updateOperationalStatus}次 - {Time.format(str(Time.getCurrentDatetime()))}")

scheduler.add_job(updateOperationalStatus, 'interval', minutes = 1)

app.include_router(ParkingFee.router)

# 排程更新 - 各縣市路邊停車費 - 系統狀態
global count_updateParkingFee_SystemStatus
count_updateParkingFee_SystemStatus = 0

async def updateParkingFee_SystemStatus():
    global count_updateParkingFee_SystemStatus
    count_updateParkingFee_SystemStatus += 1
    
    print(f"S: 更新各縣市路邊停車費 - 系統狀態 - 第{count_updateParkingFee_SystemStatus}次 - {Time.format(str(Time.getCurrentDatetime()))}")
    
    await ParkingFee.updateParkingFee_SystemStatus()
    
    print(f"E: 更新各縣市路邊停車費 - 系統狀態 - 第{count_updateParkingFee_SystemStatus}次 - {Time.format(str(Time.getCurrentDatetime()))}")

scheduler.add_job(updateParkingFee_SystemStatus, 'interval', minutes = 1)

from Website.Home.Weather import Icon, Station as WeatherStation, StationList as WeatherStationList
app.include_router(Icon.router)
app.include_router(WeatherStation.router)
app.include_router(WeatherStationList.router)

# 排程更新 - 中央氣象署 - 無人氣象測站清單
global count_updateWeatherStation
count_updateWeatherStation = 0

async def updateWeatherStation():
    global count_updateWeatherStation
    count_updateWeatherStation += 1
    
    print(f"S: 更新中央氣象署 - 無人氣象測站資料 - 第{count_updateWeatherStation}次 - {Time.format(str(Time.getCurrentDatetime()))}")
    
    await WeatherStation.updateStation()
    
    print(f"E: 更新中央氣象署 - 無人氣象測站資料 - 第{count_updateWeatherStation}次 - {Time.format(str(Time.getCurrentDatetime()))}")

scheduler.add_job(updateWeatherStation, 'interval', minutes = 10)

# 排程更新 - 中央氣象署 - 無人氣象測站清單
global count_updateWeatherStationList
count_updateWeatherStationList = 0

async def updateWeatherStationList():
    global count_updateWeatherStationList
    count_updateWeatherStationList += 1
    
    print(f"S: 更新中央氣象署 - 無人氣象測站清單 - 第{count_updateWeatherStationList}次 - {Time.format(str(Time.getCurrentDatetime()))}")
    
    await WeatherStationList.updateStationList()
    
    print(f"E: 更新中央氣象署 - 無人氣象測站清單 - 第{count_updateWeatherStationList}次 - {Time.format(str(Time.getCurrentDatetime()))}")

scheduler.add_job(updateWeatherStationList, 'interval', minutes = 1440) # 每天更新一次

from Website.Home.RoadCondition import Main as RoadCondition_Main 
from Website.Home.RoadCondition import ProvincialHighway as RoadCondition_ProvincialHighway
from Website.Home.RoadCondition import Freeway as RoadCondition_Freeway
from Website.Home.RoadCondition import LocalRoad as RoadCondition_LocalRoad

app.include_router(RoadCondition_Main.router)
app.include_router(RoadCondition_ProvincialHighway.router)
app.include_router(RoadCondition_Freeway.router)
app.include_router(RoadCondition_LocalRoad.router)

# 排程更新 - 首頁 - 路況速報
global count_updateRoadCondition
count_updateRoadCondition = 0

async def updateRoadCondition():
    global count_updateRoadCondition
    count_updateRoadCondition += 1
    
    print(f"S: 更新CMS路況速報 - 第{count_updateRoadCondition}次 - {Time.format(str(Time.getCurrentDatetime()))}")
    
    await RoadCondition_Freeway.updateRoadCondition_Freeway_CMS_List()
    await RoadCondition_Freeway.updateRoadCondition_Freeway_CMS_Content()
    await RoadCondition_Freeway.updateRoadCondition_Freeway()
    await RoadCondition_ProvincialHighway.updateRoadCondition_ProvincialHighway_CMS_List()
    await RoadCondition_ProvincialHighway.updateRoadCondition_ProvincialHighway_CMS_Content()
    await RoadCondition_ProvincialHighway.updateRoadCondition_ProvincialHighway()
    await RoadCondition_LocalRoad.updateRoadCondition_LocalRoad_CMS_List()
    await RoadCondition_LocalRoad.updateRoadCondition_LocalRoad_CMS_Content()
    await RoadCondition_LocalRoad.updateRoadCondition_LocalRoad()
    await RoadCondition_Main.updateRoadCondition()
    
    print(f"E: 更新CMS路況速報 - 第{count_updateRoadCondition}次 - {Time.format(str(Time.getCurrentDatetime()))}")

scheduler.add_job(updateRoadCondition, 'interval', minutes = 5) # 每天更新一次

from Website.Home.QuickSearch import GasStation, ConvenientStore
app.include_router(GasStation.router)
app.include_router(ConvenientStore.router)

# 2.最新消息(Website)
from Website.News import TaiwanRailway as News_TaiwanRailway
app.include_router(News_TaiwanRailway.router)

from Website.News import TaiwanHighSpeedRail as News_TaiwanHighSpeedRail
app.include_router(News_TaiwanHighSpeedRail.router)

from Website.News import MRT as News_MRT
app.include_router(News_MRT.router)

from Website.News import Bus as News_Bus
app.include_router(News_Bus.router)

from Website.News import IntercityBus as News_IntercityBus
app.include_router(News_IntercityBus.router)

from Website.News import ProvincialHighway as News_ProvincialHighway
app.include_router(News_ProvincialHighway.router)

from Website.News import LocalRoad as News_LocalRoad
app.include_router(News_LocalRoad.router)

from Website.News import TaiwanTouristShuttle as News_TaiwanTouristShuttle
app.include_router(News_TaiwanTouristShuttle.router)

from Website.News import AlishanForestRailway as News_AlishanForestRailway
app.include_router(News_AlishanForestRailway.router)

from Website.News import Freeway as News_Freeway
app.include_router(News_Freeway.router)

from Website.News import PublicBicycle as News_PublicBicycle
app.include_router(News_PublicBicycle.router)

from Website.News import Link as News_Link
app.include_router(News_Link.router)

# 排程更新TDX最新消息
global count_updateNews
count_updateNews = 0

async def updateNews():
    global count_updateNews
    count_updateNews += 1
    
    print(f"S: 更新TDX - 最新消息 - 第{count_updateNews}次 - {Time.format(str(Time.getCurrentDatetime()))}")
    
    await News_AlishanForestRailway.updateNews()
    await News_Bus.updateNews()
    await News_Freeway.updateNews()
    await News_IntercityBus.updateNews()
    await News_LocalRoad.updateNews()
    await News_MRT.updateNews()
    await News_ProvincialHighway.updateNews()
    await News_PublicBicycle.updateNews()
    await News_TaiwanHighSpeedRail.updateNews()
    await News_TaiwanRailway.updateNews()
    await News_TaiwanTouristShuttle.updateNews()
    
    print(f"E: 更新TDX - 最新消息 - 第{count_updateNews}次 - {Time.format(str(Time.getCurrentDatetime()))}")

scheduler.add_job(updateNews, 'interval', minutes = 5)

# 3.即時訊息推播(Website)
from Website.CMS import CRUD, ServiceArea
app.include_router(CRUD.router)
app.include_router(ServiceArea.router)

# 4-1.道路資訊(Website)
from Website.Information.Road import Main,CityCarPark_ParkingNum,CityCarPark_ParkingInfo,RoadInfo_Road_Construction,RoadInfo_Accident,RoadInfo_Trafficjam,RoadInfo_Traffic_Control
app.include_router(Main.router)
app.include_router(CityCarPark_ParkingNum.router)
app.include_router(CityCarPark_ParkingInfo.router)
app.include_router(RoadInfo_Road_Construction.router)
app.include_router(RoadInfo_Accident.router)
app.include_router(RoadInfo_Trafficjam.router)
app.include_router(RoadInfo_Traffic_Control.router)

from Website.Information.Road.Parking.OnStreet import Taichung
app.include_router(Taichung.router)

# 4-2.大眾運輸資訊(Website)
from Website.Information.PublicTransport import PublicBicycle,InterCityBusRoute
app.include_router(PublicBicycle.router)
app.include_router(InterCityBusRoute.router)

from Website.Information.PublicTransport.Bus import StopOfRoute, Route
app.include_router(StopOfRoute.router)
app.include_router(Route.router)

from Website.Information.PublicTransport.TaiwanRailway import Station
app.include_router(Station.router)

# 5.觀光資訊(Website)
from Website.Information.Tourism import Activity, Hotel, Parking, Restaurant, ScenicSpot
app.include_router(Activity.router)
app.include_router(Hotel.router)
app.include_router(Parking.router)
app.include_router(Restaurant.router)
app.include_router(ScenicSpot.router)

# 排程更新TDX最新消息
global count_updateTourismData
count_updateTourismData = 0

async def updateTourismData():
    global count_updateTourismData
    count_updateTourismData += 1
    
    print(f"S: 更新TDX - 觀光資訊 - 第{count_updateTourismData}次 - {Time.format(str(Time.getCurrentDatetime()))}")
    
    await Activity.update()
    await Hotel.update()
    await Parking.update()
    await Restaurant.update()
    await ScenicSpot.update()
    
    print(f"E: 更新TDX - 觀光資訊 - 第{count_updateTourismData}次 - {Time.format(str(Time.getCurrentDatetime()))}")

scheduler.add_job(updateTourismData, 'interval', minutes = 40)


# ---------------------------------------------------------------

# 通用功能
from Universal import Logo, API
app.include_router(API.router)
app.include_router(Logo.router)

# ---------------------------------------------------------------
