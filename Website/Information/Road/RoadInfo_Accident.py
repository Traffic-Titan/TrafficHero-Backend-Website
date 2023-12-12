from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
import requests

router = APIRouter(tags=["4-1.道路資訊(Website)"],prefix="/Website/Information/Road")

@router.put("/RoadInfo_Accident",summary="【Update】道路資訊-PBS-事故")
async def RoadInfo_Accident(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 警廣即時路況\n
            	https://data.gov.tw/dataset/15221 \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證    

    return await updateInfo()

async def updateInfo():
    collection = await MongoDB.getCollection("traffic_hero","information_road_info_pbs_accident")
    
    collection.drop() # 刪除該collection所有資料
    documents = []

    try:
        url = "https://data.moi.gov.tw/MoiOD/System/DownloadFile.aspx?DATA=36384FA8-FACF-432E-BB5B-5F015E7BC1BE"
        response = requests.get(url)
        PBS_data = response.json()

        for data in PBS_data:
            if(data['roadtype'] == "事故"):
                documents.append(data)
    except Exception as e:
        print(e)
         
    collection.insert_many(documents)

    return f"已更新筆數:{collection.count_documents({})}"