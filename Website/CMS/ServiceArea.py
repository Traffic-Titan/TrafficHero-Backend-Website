from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from PIL import Image
import os
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
import Website.CMS.MainContent as CMS_MainContent
from datetime import datetime, timedelta
import requests

router = APIRouter(tags=["3.即時訊息推播(Website)"],prefix="/Website/CMS")

@router.put("/ServiceArea/ParkingStatus", summary="【Update】即時訊息推播-高速公路服務區停車位狀態")
async def service_area_parking_status(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 即時路況 - 交通部高速公路局
                https://1968.freeway.gov.tw/ \n
            2. 交通部運輸資料流通服務平臺(TDX) - 全臺高速公路服務區停車場剩餘位資料 v1
                https://tdx.transportdata.tw/api-service/swagger/basic/945f57da-f29d-4dfd-94ec-c35d9f62be7d#/FreewayCarPark/ParkingApi_ParkingFreewayAvailability \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    # 取得剩餘停車位數
    url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/Road/Freeway/ServiceArea?%24format=JSON" 
    dataAll = TDX.getData(url)
    available_spaces = {}
    for service in dataAll["ParkingAvailabilities"]:
        available_spaces.update({service["CarParkName"]["Zh_tw"]: str(service["AvailableSpaces"])})

    # 取得1968資料
    data = requests.get(f'https://1968.freeway.gov.tw/getServiceAreasInfo?action=sa&area=A').json()
    for d in data["response"]:
        if d["service_name"] in ["楊梅休息站", "關西服務區", "清水服務區", "南投服務區", "古坑服務區", "東山服務區", "石碇服務區"]:
            d["available"] = available_spaces[d["service_name"]]
    
    collection = MongoDB.getCollection("traffic_hero","service_area_parking_status") # 取得MongoDB的collection
    collection.delete_many({}) # 清空collection
    collection.insert_many(data["response"])
     
    def parkingLevelToStatus(parkingLevel):
        match parkingLevel:
            case "green":
                return "未滿"
            case "yellow":
                return "將滿"
            case "red": 
                return "已滿"
            case _:
                return "無資料"
    
    for result in collection.find({}, {"_id": 0}): # Demo
        if "available" in result:
            status = parkingLevelToStatus(result['parkingLevel'])
            content = {
                "type": "高速公路服務區停車位狀態",
                "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/ROC_Taiwan_Area_National_Freeway_Bureau_Logo.svg/200px-ROC_Taiwan_Area_National_Freeway_Bureau_Logo.svg.png",
                "content": [
                    {
                        "text": [f"{result['service_name']}"],
                        "color": ["#FFFFFF"]
                    },
                    {
                        "text": [f"狀態:",status],
                        "color": ["#FFFFFF","#FFFFFF"]
                    },
                    {
                        "text": [f"尚有{result['available']}格停車位"],
                        "color": ["#FFFFFF"]
                    }
                ],
                "voice": f"前方{result['service_name']}，目前還有{result['available']}格停車位，停車位{status}",
                "location": {
                    "longitude": "121.000000", # Demo
                    "latitude": "25.000000", # Demo
                },
                "direction": "string", # Demo
                "distance": 2.5,
                "priority": "1", # Demo
                "start": datetime.now(),
                "end": datetime.now() + timedelta(minutes = 10),
                "active": True,
                "id": "string"
                }
        else:
            content = {
                "type": "高速公路服務區停車位狀態",
                "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/ROC_Taiwan_Area_National_Freeway_Bureau_Logo.svg/200px-ROC_Taiwan_Area_National_Freeway_Bureau_Logo.svg.png",
                "content": [
                    {
                        "text": [f"{result['service_name']}"],
                        "color": ["#FFFFFF"]
                    },
                    {
                        "text": [f"狀態:",status],
                        "color": ["#FFFFFF","#FFFFFF"]
                    }
                ],
                "voice": f"前方{result['service_name']}，停車位{status}",
                "location": {
                    "longitude": "121.000000", # Demo
                    "latitude": "25.000000", # Demo
                },
                "direction": "string", # Demo
                "distance": 2.5,
                "priority": "1", # Demo
                "start": datetime.now(),
                "end": datetime.now() + timedelta(minutes = 10),
                "active": True,
                "id": "string"
                }

        CMS_MainContent.create("car", content)
 
    return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}




    # chrome_options = webdriver.ChromeOptions() # 創建設定實例
    # chrome_options.add_argument('--window-size=1920,1080')  # 指定解析度
    # driver = webdriver.Chrome(options=chrome_options)

    # driver.get("https://1968.freeway.gov.tw/") # 打開「即時路況 - 交通部高速公路局」網站
    # time.sleep(3) # 等待3秒，讓網站完全載入
    # driver.save_screenshot("screenshot.png") # 截圖並儲存為screenshot.png
    # driver.quit() # 關閉瀏覽器

    # screenshot = Image.open("screenshot.png") # 打開截圖

    # serviceArea = {
    #     # 國道一號
    #     "中壢服務區(南北向)" : (1170, 221),
    #     "楊梅休息站(南向)" : (1158, 236),
    #     "湖口服務區(南向)" : (1138, 248),
    #     "湖口服務區(北向)" : (1150, 260),
    #     "泰安服務區(南向)" : (1077, 350),
    #     "泰安服務區(北向)" : (1096, 361),
    #     "西螺服務區(南向)" : (1035, 465),
    #     "西螺服務區(北向)" : (1052, 468),
    #     "新營服務區(南向)" : (1000, 555),
    #     "新營服務區(北向)" : (1020, 565),
    #     "仁德服務區(南向)" : (995, 650),
    #     "仁德服務區(北向)" : (1010, 645),
        
    #     # 國道三號
    #     "木柵休息站(北向)" : (1241, 242),
    #     "關西服務區(南北向)" : (1165, 260),
    #     "寶山休息站(南向)" : (1143, 285),
    #     "西湖服務區(南向)" : (1090, 310),
    #     "西湖服務區(北向)" : (1100, 315),
    #     "清水服務區(南北向)" : (1070, 375),
    #     "南投服務區(南北向)" : (1090, 443),
    #     "古坑服務區(南北向)" : (1060, 510),
    #     "東山服務區(南北向)" : (1040, 570),
    #     "新化休息站(南向)" : (1010, 623),
    #     "新化休息站(北向)" : (1020, 615),
    #     "關廟服務區(南向)" : (1019, 631),
    #     "關廟服務區(北向)" : (1025, 635),
        
    #     # 國道五號
    #     "石碇服務區(南北向)" : (1258, 233),
    #     "蘇澳服務區(南北向)" : (1281, 304),
    # }
    
    # def getStatus(name):
    #     x = serviceArea[name][0]
    #     y = serviceArea[name][1]
    #     color = screenshot.getpixel((x, y))
    #     # print(f"{name}: 位置 ({x}, {y}) 的顏色：{color}") # Dev
    #     match color:
    #         case (0, 104, 55, 255):
    #             return "未滿" # 綠色-未滿
    #         case (251, 176, 59, 255):
    #             return "將滿" # 黃色-將滿
    #         case (232, 10, 21, 255):
    #             return "已滿" # 紅色-已滿
    #         case _:
    #             return "無資料" # 無資料

    
    # # 取得剩餘停車位數
    # url = "https://tdx.transportdata.tw/api/basic/v1/Parking/OffStreet/ParkingAvailability/Road/Freeway/ServiceArea?%24format=JSON" 
    # dataAll = TDX.getData(url)
    # available_spaces = {}
    # for service in dataAll["ParkingAvailabilities"]:
    #     available_spaces.update({service["CarParkName"]["Zh_tw"]: str(service["AvailableSpaces"])})

    # data = [
    #     # 國道一號
    #     {"name": "中壢服務區", "type": "南北向", "status": getStatus("中壢服務區(南北向)")},
    #     {"name": "楊梅休息站", "type": "南向", "status": getStatus("楊梅休息站(南向)"), "available": available_spaces["楊梅休息站"]},
    #     {"name": "湖口服務區", "type": "南向", "status": getStatus("湖口服務區(南向)")},
    #     {"name": "湖口服務區", "type": "北向", "status": getStatus("湖口服務區(北向)")},
    #     {"name": "泰安服務區", "type": "南向", "status": getStatus("泰安服務區(南向)")},
    #     {"name": "泰安服務區", "type": "北向", "status": getStatus("泰安服務區(北向)")},
    #     {"name": "西螺服務區", "type": "南向", "status": getStatus("西螺服務區(南向)")},
    #     {"name": "西螺服務區", "type": "北向", "status": getStatus("西螺服務區(北向)")},
    #     {"name": "新營服務區", "type": "南向", "status": getStatus("新營服務區(南向)")},
    #     {"name": "新營服務區", "type": "北向", "status": getStatus("新營服務區(北向)")},
    #     {"name": "仁德服務區", "type": "南向", "status": getStatus("仁德服務區(南向)")},
    #     {"name": "仁德服務區", "type": "北向", "status": getStatus("仁德服務區(北向)")},
        
    #     # 國道三號
    #     {"name": "木柵休息站", "type": "北向", "status": getStatus("木柵休息站(北向)")},
    #     {"name": "關西服務區", "type": "南北向", "status": getStatus("關西服務區(南北向)"), "available": available_spaces["關西服務區"]},
    #     {"name": "寶山休息站", "type": "南向", "status": getStatus("寶山休息站(南向)")},
    #     {"name": "西湖服務區", "type": "南向", "status": getStatus("西湖服務區(南向)")},
    #     {"name": "西湖服務區", "type": "北向", "status": getStatus("西湖服務區(北向)")},
    #     {"name": "清水服務區", "type": "南北向", "status": getStatus("清水服務區(南北向)"), "available": available_spaces["清水服務區"]},
    #     {"name": "南投服務區", "type": "南北向", "status": getStatus("南投服務區(南北向)"), "available": available_spaces["南投服務區"]},
    #     {"name": "古坑服務區", "type": "南北向", "status": getStatus("古坑服務區(南北向)"), "available": available_spaces["古坑服務區"]},
    #     {"name": "東山服務區", "type": "南北向", "status": getStatus("東山服務區(南北向)"), "available": available_spaces["東山服務區"]},
    #     {"name": "新化休息站", "type": "南向", "status": getStatus("新化休息站(南向)")},
    #     {"name": "新化休息站", "type": "北向", "status": getStatus("新化休息站(北向)")},
    #     {"name": "關廟服務區", "type": "南向", "status": getStatus("關廟服務區(南向)")},
    #     {"name": "關廟服務區", "type": "北向", "status": getStatus("關廟服務區(北向)")},
        
    #     # 國道五號
    #     {"name": "石碇服務區", "type": "南北向", "status": getStatus("石碇服務區(南北向)"), "available": available_spaces["石碇服務區"]},
    #     {"name": "蘇澳服務區", "type": "南北向", "status": getStatus("蘇澳服務區(南北向)")},
    # ]

    # collection = MongoDB.getCollection("traffic_hero","service_area_parking_status") # 取得MongoDB的collection
    # collection.delete_many({}) # 清空collection
    # collection.insert_many(data)

    # os.remove("screenshot.png") # 刪除截圖