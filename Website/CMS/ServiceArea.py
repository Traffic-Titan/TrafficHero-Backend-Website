from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from selenium import webdriver
import time
from PIL import Image
import os

router = APIRouter(tags=["3.即時訊息推播(Website)"],prefix="/Website/CMS")

@router.get("/ServiceArea")
async def service_area(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 即時路況 - 交通部高速公路局
                https://1968.freeway.gov.tw/ \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    chrome_options = webdriver.ChromeOptions() # 創建設定實例
    chrome_options.add_argument('--window-size=1920,1080')  # 指定解析度
    # driver = webdriver.Chrome(executable_path="chromedriver.exe", chrome_options=chrome_options) # 創建Chrome瀏覽器實例 (Dev for Windows)
    driver = webdriver.Chrome(chrome_options=chrome_options) # 創建Chrome瀏覽器實例 (Dev for Linux)

    driver.get("https://1968.freeway.gov.tw/") # 打開「即時路況 - 交通部高速公路局」網站
    time.sleep(3) # 等待3秒，讓網站完全載入
    driver.save_screenshot("screenshot.png") # 截圖並儲存為screenshot.png
    driver.quit() # 關閉瀏覽器

    screenshot = Image.open("screenshot.png") # 打開截圖

    serviceArea = {
        # 國道一號
        "中壢服務區(南北向)" : (1170, 221),
        "楊梅休息站(南向)" : (1158, 236),
        "湖口服務區(南向)" : (1138, 248),
        "湖口服務區(北向)" : (1150, 260),
        "泰安服務區(南向)" : (1083, 352),
        "泰安服務區(北向)" : (1095, 360),
        "西螺服務區(南向)" : (1035, 465),
        "西螺服務區(北向)" : (1050, 465),
        "新營服務區(南向)" : (1000, 555),
        "新營服務區(北向)" : (1020, 565),
        "仁德服務區(南向)" : (995, 650),
        "仁德服務區(北向)" : (1010, 645),
        
        # 國道三號
        "木柵休息站(北向)" : (1241, 242),
        "關西服務區(南北向)" : (1165, 260),
        "寶山休息站(南向)" : (1143, 285),
        "西湖服務區(南向)" : (1090, 310),
        "西湖服務區(北向)" : (1100, 315),
        "清水服務區(南北向)" : (1070, 375),
        "南投服務區(南北向)" : (1090, 443),
        "古坑服務區(南北向)" : (1060, 510),
        "東山服務區(南北向)" : (1040, 570),
        "新化休息站(南向)" : (1010, 623),
        "新化休息站(北向)" : (1020, 615),
        "關廟服務區(南向)" : (1019, 631),
        "關廟服務區(北向)" : (1025, 635),
        
        # 國道五號
        "石碇服務區(南北向)" : (1258, 233),
        "蘇澳服務區(南北向)" : (1281, 304),
    }

    parking_status = {}
    for key, value in serviceArea.items():
        x = value[0]
        y = value[1]
        color = screenshot.getpixel((x, y))
        # print(f"位置 ({x}, {y}) 的顏色：{color}") # Dev
        match color:
            case (0, 104, 55, 255):
                parking_status.update({key: "未滿"}) # 綠色-未滿
            case (251, 176, 59, 255):
                parking_status.update({key: "將滿"}) # 黃色-將滿
            case (232, 10, 21, 255):
                parking_status.update({key: "已滿"}) # 紅色-已滿
            case _:
                parking_status.update({key: "無資料"}) # 無資料

    result = {
        "service_area_parking_status": parking_status,
    }

    os.remove("screenshot.png") # 刪除截圖
 
    return result
