from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
from bson import ObjectId
import Service.TDX as TDX
import requests
import xml.etree.ElementTree as ET

router = APIRouter(tags=["1.首頁(Website)"],prefix="/Website/Home")

@router.put("/QuickSearch/GasStation",summary="【Update】快速尋找地點-加油站列表")
async def updateGasStationListAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1. 政府資料開放平臺 - 加油站服務資訊
                https://data.gov.tw/dataset/6065 \n
        二、Input \n
                1. 
        三、Output \n
                1. 
        四、說明 \n
                1.
        """
        Token.verifyToken(token.credentials,"admin") # JWT驗證
        return updateGasStationList()

def updateGasStationList():
        collection = MongoDB.getCollection("traffic_hero","gas_station_list")
        
        try:
                # XML資料的網址
                url = "https://vipmbr.cpc.com.tw/CPCSTN/STNWebService.asmx/getStationInfo_XML"

                # 發送HTTP GET請求取得XML資料
                response = requests.get(url)

                if response.status_code == 200:
                        # 解析XML資料
                        root = ET.fromstring(response.text)
                        
                        documents = []
                        # 遍歷XML中的每個Table元素
                        for table in root.findall(".//Table"):
                                station_data = {}
                                for element in table:
                                        station_data[element.tag] = element.text
                                        
                                station_data['營業中'] = True if table.find("營業中").text == "1" else False
                                station_data['國道高速公路'] = True if table.find("國道高速公路").text == "1" else False
                                station_data['無鉛92'] = True if table.find("無鉛92").text == "1" else False
                                station_data['無鉛95'] = True if table.find("無鉛95").text == "1" else False
                                station_data['無鉛98'] = True if table.find("無鉛98").text == "1" else False
                                station_data['酒精汽油'] = True if table.find("酒精汽油").text == "1" else False
                                station_data['煤油'] = True if table.find("煤油").text == "1" else False
                                station_data['超柴'] = True if table.find("超柴").text == "1" else False
                                station_data['會員卡'] = True if table.find("會員卡").text == "1" else False
                                station_data['刷卡自助'] = True if table.find("刷卡自助").text == "1" else False
                                station_data['自助柴油站'] = True if table.find("自助柴油站").text == "1" else False
                                station_data['電子發票'] = True if table.find("電子發票").text == "1" else False
                                station_data['悠遊卡'] = True if table.find("悠遊卡").text == "1" else False
                                station_data['一卡通'] = True if table.find("一卡通").text == "1" else False
                                station_data['HappyCash'] = True if table.find("HappyCash").text == "1" else False
                                
                                station_data["position"] = {"longitude": float(station_data["經度"]), "latitude": float(station_data["緯度"])}
                                del station_data["經度"]
                                del station_data["緯度"]
                                
                                station_data['_id'] = ObjectId()
                                documents.append(station_data)

                        collection.drop() # 刪除該collection所有資料
                        collection.insert_many(documents)
                        return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}
