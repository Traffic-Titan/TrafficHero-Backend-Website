"""
1. 目前設定為每次啟動時，會將資料庫清空，並重新抓取資料，以後必需按照來源狀況，設定更新資料的時間  
"""
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from api_analytics.fastapi import Analytics
from Service.Database import MongoDBSingleton
import Function.Time as Time
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware

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
scheduler = BackgroundScheduler() # 排程器

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
from Website.Home import OperationalStatus
app.include_router(OperationalStatus.router)

from Website.Home.Weather import Icon, Station as WeatherStation, StationList as WeatherStationList
app.include_router(Icon.router)
app.include_router(WeatherStation.router)
app.include_router(WeatherStationList.router)

# 排程更新 - 中央氣象署 - 無人氣象測站清單
global count_updateWeatherStation
count_updateWeatherStation = 0

def updateWeatherStation():
    global count_updateWeatherStation
    count_updateWeatherStation += 1
    
    print(f"S: 更新中央氣象署 - 無人氣象測站資料 - 第{count_updateWeatherStation}次 - {Time.format(str(Time.getCurrentDatetime()))}")
    
    WeatherStation.updateStation()
    
    print(f"E: 更新中央氣象署 - 無人氣象測站資料 - 第{count_updateWeatherStation}次 - {Time.format(str(Time.getCurrentDatetime()))}")

scheduler.add_job(updateWeatherStation, 'interval', minutes = 10)

# 排程更新 - 中央氣象署 - 無人氣象測站清單
global count_updateWeatherStationList
count_updateWeatherStationList = 0

def updateWeatherStationList():
    global count_updateWeatherStationList
    count_updateWeatherStationList += 1
    
    print(f"S: 更新中央氣象署 - 無人氣象測站清單 - 第{count_updateWeatherStationList}次 - {Time.format(str(Time.getCurrentDatetime()))}")
    
    WeatherStationList.updateStationList()
    
    print(f"E: 更新中央氣象署 - 無人氣象測站清單 - 第{count_updateWeatherStationList}次 - {Time.format(str(Time.getCurrentDatetime()))}")

scheduler.add_job(updateWeatherStationList, 'interval', minutes = 1440) # 每天更新一次

from Website.Home.RoadCondition import Main, ProvincialHighway, Freeway, LocalRoad
app.include_router(Main.router)
app.include_router(ProvincialHighway.router)
app.include_router(Freeway.router)
app.include_router(LocalRoad.router)

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

def updateNews():
    global count_updateNews
    count_updateNews += 1
    
    print(f"S: 更新TDX - 最新消息 - 第{count_updateNews}次 - {Time.format(str(Time.getCurrentDatetime()))}")
    
    News_AlishanForestRailway.updateNews()
    News_Bus.updateNews()
    News_Freeway.updateNews()
    News_IntercityBus.updateNews()
    News_LocalRoad.updateNews()
    News_MRT.updateNews()
    News_ProvincialHighway.updateNews()
    News_PublicBicycle.updateNews()
    News_TaiwanHighSpeedRail.updateNews()
    News_TaiwanRailway.updateNews()
    News_TaiwanTouristShuttle.updateNews()
    
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
from Website.Information.Tourism import TouristSpot,TouristHotel,TouristActivity,TouristFood,TouristParking
app.include_router(TouristSpot.router)
app.include_router(TouristHotel.router)
app.include_router(TouristActivity.router)
app.include_router(TouristFood.router)
app.include_router(TouristParking.router)

# 排程更新TDX最新消息
global count_updateTourismData
count_updateTourismData = 0

def updateTourismData():
    global count_updateTourismData
    count_updateTourismData += 1
    
    print(f"S: 更新TDX - 觀光資訊 - 第{count_updateTourismData}次 - {Time.format(str(Time.getCurrentDatetime()))}")
    
    TouristActivity.updateTouristActivity()
    TouristFood.updateTouristFood()
    TouristHotel.updateTouristHotel()
    TouristParking.updateTouristParking()
    TouristSpot.updateTouristSpot()
    
    print(f"E: 更新TDX - 觀光資訊 - 第{count_updateTourismData}次 - {Time.format(str(Time.getCurrentDatetime()))}")

scheduler.add_job(updateTourismData, 'interval', minutes = 1440) # 每天更新一次


# ---------------------------------------------------------------

# 通用功能
from Universal import Logo, API
app.include_router(API.router)
app.include_router(Logo.router)

# ---------------------------------------------------------------

# #每天0點0分定時執行Function
# def setInterval(function):
#     #現在時間
#     now_time = datetime.datetime.now()

#     #明天時間
#     next_time = now_time + datetime.timedelta(days=+1)
#     next_year = next_time.date().year
#     next_month = next_time.date().month
#     next_day = next_time.date().day

#     #獲取明天0點0分時間
#     next_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" 00:00:00","%Y-%m-%d %H:%M:%S")

#     #獲取距離明天0點0分的時間 , 單位時間"秒"
#     timerStartTime = (next_time - now_time).total_seconds()

#     timer = threading.Timer(timerStartTime,function)
#     timer.start()
    
#檢查目前資料庫內的版本與最新的版本有沒有差異，若有的話，通知User更新
# def CheckUpdate_SpeedEnforcement():
#     #連接DataBase
#     # 0715：MongoDB.getCollection()後面的Collection名稱沒辦法當變數
#     Collection = MongoDB.getCollection("Speed_Enforcement")

#     #讀取DataBase內的資料，並存進document
#     document = []
#     count = 0
#     for info in Collection.find({}):
#         document.append(info)
#     #判斷Speed_Enforcement.getData()的經緯度 與 document的經緯度 有無相同。如果全部相同，count應為 2098
#     for speedEnforcement in Speed_Enforcement.getData():
#         for doc in document:
#             if((speedEnforcement['Latitude'],speedEnforcement['Longitude']) == (doc['Latitude'],doc['Longitude'])):
#                 count = count + 1
#     if(count == 2098):
#         print("資料同步")
#     else:
#         print("資料需要更新")
