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
                                station_data['_id'] = ObjectId()
                                documents.append(station_data)

                        collection.drop() # 刪除該collection所有資料
                        collection.insert_many(documents)
                        return {"message": f"更新成功，總筆數:{collection.count_documents({})}"}
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}