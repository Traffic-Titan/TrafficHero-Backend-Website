from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
import Function.Weather as Weather

router = APIRouter(tags=["5.觀光資訊(Website)"],prefix="/Website/Information")

@router.put("/Tourism/Hotel",summary="【Update】觀光景點-全臺觀光景點飯店")
async def updateAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """
        一、資料來源: \n
                1. 交通部運輸資料流通服務平臺(TDX) - 取得所有觀光旅宿資料
                https://tdx.transportdata.tw/api-service/swagger/basic/cd0226cf-6292-4c35-8a0d-b595f0b15352#/Tourism/TourismApi_Hotel_2244 \n
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
        collection = await MongoDB.getCollection("traffic_hero","tourism_hotel")
        try:
                url = f"https://tdx.transportdata.tw/api/basic/v2/Tourism/Hotel?%24format=JSON" # 取得資料來源網址
                data = TDX.getData(url) # 取得資料

                documents = []
                for d in data:
                        d["id"] = d.pop("HotelID")
                        d["name"] = d.pop("HotelName")
                        d["description"] = d.pop("Description") if d.get("Description") != None else ""
                        d["grade"] = d.pop("Grade") if d.get("Grade") != None else ""
                        d["address"] = d.pop("Address") if d.get("Address") != None else ""
                        d["zip_code"] = d.pop("ZipCode") if d.get("ZipCode") != None else ""
                        d["phone"] = d.pop("Phone") if d.get("Phone") != None else ""
                        d["fax"] = d.pop("Fax") if d.get("Fax") != None else ""
                        d["website_url"] = d.pop("WebsiteUrl") if d.get("WebsiteUrl") != None else ""
                        
                        if "Picture" in d:
                                picture_urls = []
                                for i in range(1, 4):
                                        key = f"PictureUrl{i}"
                                        if key in d["Picture"]:
                                                picture_urls.append(d["Picture"][key])
                                d["picture"] = picture_urls if len(picture_urls) > 0 else ["https://cdn3.iconfinder.com/data/icons/basic-2-black-series/64/a-92-256.png"]
                                del d["Picture"]
                        
                        if "Position" in d:
                                d["position"] = {
                                        "longitude": d["Position"]["PositionLon"],
                                        "latitude": d["Position"]["PositionLat"]
                                }
                                del d["Position"]
                        
                        d["class"] = d.pop("Class") if d.get("Class") != None else ""
                        d["map_url"] = d.pop("MapUrl") if d.get("MapUrl") != None else ""
                        d["spec"] = d.pop("Spec") if d.get("Spec") != None else ""
                        d["service_info"] = d.pop("ServiceInfo") if d.get("ServiceInfo") != None else ""
                        d["parking_info"] = d.pop("ParkingInfo") if d.get("ParkingInfo") != None else ""
                        d["city"] = d.pop("City") if d.get("City") != None else ""
                        d["src_update_time"] = d.pop("SrcUpdateTime") if d.get("SrcUpdateTime") != None else ""
                        d["update_time"] = d.pop("UpdateTime") if d.get("UpdateTime") != None else ""
                        
                        d["weather"] = await Weather.getWeather(d["position"]["longitude"],d["position"]["latitude"])
                        
                        documents.append(d)
                        
                await collection.drop() # 刪除該collection所有資料
                await collection.insert_many(documents) # 將資料存入MongoDB
        except Exception as e:
                return {"message": f"更新失敗，錯誤訊息:{e}"}

        return {"message": f"更新成功，總筆數:{await collection.count_documents({})}"}

