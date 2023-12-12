import requests
import math
from scipy.spatial import distance
from Main import MongoDB # 引用MongoDB連線實例
import Function.Time as Time
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import time

async def getWeather(longitude: str, latitude: str):
    try:
        collection = await MongoDB.getCollection("traffic_hero","weather_station") # 取得無人氣象測站資料
        pipeline = [ # 使用Aggregation Pipeline找到最近的氣象站
            {
                "$project": {
                    "_id": 0,
                    "stationId": 1,
                    "name": 1,
                    "lat": 1,
                    "lon": 1,
                    "distance": {
                        "$sqrt": {
                            "$add": [
                                { "$pow": [ { "$subtract": [ { "$toDouble": "$lat" }, float(latitude) ] }, 2 ] },
                                { "$pow": [ { "$subtract": [ { "$toDouble": "$lon" }, float(longitude) ] }, 2 ] }
                            ]
                        }
                    },
                    "locationName": 1,
                    "weatherElement": 1,
                    "parameter": 1
                }
            },
            {
                "$sort": {"distance": 1}
            },
            {
                "$limit": 1
            }
        ]

        weather_station = list(collection.aggregate(pipeline))[0]
        
        the_lowest_temperature = float(weather_station["weatherElement"][12]["elementValue"]) # 最低溫
        the_highest_temperature = float(weather_station["weatherElement"][10]["elementValue"]) # 最高溫
        temperature = float(weather_station["weatherElement"][3]["elementValue"]) # 目前溫度
        weather = weather_station["weatherElement"][14]["elementValue"] # 目前氣象描述
        # station_name = weather_station["locationName"] # 觀測站名稱
        # station_id = weather_station["stationId"] # 觀測站名稱
        
        if temperature != -99:
            # 根據系統時間判斷白天或晚上(以後可改成根據日出日落時間判斷)
            currentTime = datetime.now() + timedelta(hours=8) # 取得目前的時間(轉換成台灣時間，伺服器時區為UTC+0)
            
            if 6 <= currentTime.hour < 18:
                type = "day"
            else:
                type = "night"
            
            collection = await MongoDB.getCollection("traffic_hero","weather_icon") # 取得天氣圖示URL 
            weather_icon =  await collection.find_one({"weather": weather},{"_id":0,f"icon_url_{type}":1}) 
            weather_icon_url = weather_icon.get(f"icon_url_{type}") if weather_icon and weather_icon.get(f"icon_url_{type}") else "https://cdn3.iconfinder.com/data/icons/basic-2-black-series/64/a-92-256.png" # 預設
            
            result = {
                "temperature": round(temperature),
                "the_lowest_temperature": round(the_lowest_temperature),
                "the_highest_temperature": round(the_highest_temperature),
                "weather": weather,
                "weather_icon_url": weather_icon_url
                # "觀測站": station_name, # (Dev)
                # "觀測站ID": station_id # (Dev)
            }
        else:
            result = None
            
        return result
    except Exception as e:
        return None
