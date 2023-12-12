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
        return await updateGasStationList()

async def updateGasStationList():
        collection = await MongoDB.getCollection("traffic_hero","gas_station_list")
        
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
                                basic = {
                                        "station_code": table.find("站代號").text,
                                        "type": table.find("類別").text,
                                        "station_name": table.find("站名").text,
                                        "address": table.find("縣市").text + table.find("鄉鎮區").text + table.find("地址").text,
                                        "phone": table.find("電話").text,
                                        "available": True if table.find("營業中").text == "1" else False,
                                        "in_freeway": True if table.find("國道高速公路").text == "1" else False,
                                        "business_hours": table.find("營業時間").text
                                }
                                
                                gasoline = {
                                        "92": True if table.find("無鉛92").text == "1" else False,
                                        "95": True if table.find("無鉛95").text == "1" else False,
                                        "98": True if table.find("無鉛98").text == "1" else False,
                                        "alcohol_gasoline": True if table.find("酒精汽油").text == "1" else False,
                                        "kerosene": True if table.find("煤油").text == "1" else False,
                                        "super_diesel": True if table.find("超柴").text == "1" else False
                                }
                                
                                payment = {
                                        "member_card": True if table.find("會員卡").text == "1" else False,
                                        "e_invoice": True if table.find("電子發票").text == "1" else False,
                                        "easy_card": True if table.find("悠遊卡").text == "1" else False,
                                        "i_pass": True if table.find("一卡通").text == "1" else False,
                                        "happy_cash": True if table.find("HappyCash").text == "1" else False
                                }
                                
                                other_service = {
                                        "self_service": True if table.find("刷卡自助").text == "1" else False,
                                        "self_service_diesel": True if table.find("自助柴油站").text == "1" else False,
                                        "car_wash": table.find("洗車類別").text,
                                        "etag": table.find("etag申裝儲值時間").text,
                                        "maintenance": table.find("保養間時間").text
                                }
                                
                                location = {
                                        "longitude": float(table.find("經度").text),
                                        "latitude": float(table.find("緯度").text)
                                }
                                
                                        
                                data = {
                                        "basic": basic,
                                        "gasoline": gasoline,
                                        "payment": payment,
                                        "other_service": other_service,
                                        "location": location,
                                        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/CPC_Corporation%2C_Taiwan_Seal.svg/1024px-CPC_Corporation%2C_Taiwan_Seal.svg.png"
                                }
                                
                                documents.append(data)

                        await collection.drop() # 刪除該collection所有資料
                        await collection.insert_many(documents)
                        return {"message": f"更新成功，總筆數:{await collection.count_documents({})}"}
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}


# <Table>
# <站代號>AA6212A03</站代號>
# <類別>加盟站</類別>
# <站名>台東</站名>
# <縣市>台東縣</縣市>
# <鄉鎮區>台東市</鄉鎮區>
# <地址>豐谷里15鄰中華路二段515號</地址>
# <電話>(089)343542</電話>
# <服務中心>D611C</服務中心>
# <營業中>1</營業中>
# <國道高速公路>0</國道高速公路>
# <無鉛92>1</無鉛92>
# <無鉛95>1</無鉛95>
# <無鉛98>0</無鉛98>
# <酒精汽油>0</酒精汽油>
# <煤油>0</煤油>
# <超柴>1</超柴>
# <會員卡>1</會員卡>
# <刷卡自助>0</刷卡自助>
# <自助柴油站>0</自助柴油站>
# <電子發票>1</電子發票>
# <悠遊卡>0</悠遊卡>
# <一卡通>0</一卡通>
# <HappyCash>0</HappyCash>
# <經度>121.131802</經度>
# <緯度>22.741134</緯度>
# <營業時間>06:30-21:30</營業時間>
# <洗車類別> </洗車類別>
# <etag申裝儲值時間> </etag申裝儲值時間>
# <保養間時間> </保養間時間>
# </Table>





# {
#   "basic": {
#     "code": "AA6212A03",
#     "type": "加盟站",
#     "station_name": "台東",
#     "address": "台東縣台東市豐谷里15鄰中華路二段515號",
#     "phone": "(089)343542",
#     "available": true,
#     "in_freeway": false,
#     "營業時間": "06:30-21:30"
#   },
#   "gasoline": {
#     "92": true,
#     "95": true,
#     "98": false,
#     "酒精汽油": false,
#     "煤油": false,
#     "超柴": true
#   },
#   "payment": {
#     "會員卡": true,
#     "刷卡自助": false,
#     "電子發票": true,
#     "悠遊卡": false,
#     "一卡通": false,
#     "HappyCash": false
#   },
#   "other_service": {
#     "自助柴油站": false,
#     "洗車類別": "\n    ",
#     "etag申裝儲值時間": "\n    ",
#     "保養間時間": "\n    "
#   },
#   "position": {
#     "longitude": 121.131802,
#     "latitude": 22.741134
#   }  
# }