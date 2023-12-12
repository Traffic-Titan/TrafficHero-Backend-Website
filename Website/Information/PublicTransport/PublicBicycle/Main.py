from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from pymongo import UpdateOne
from collections import OrderedDict

router = APIRouter(tags=["4-2.大眾運輸資訊(Website)"],prefix="/Website/Information/PublicTransport")

@router.put("/PublicBicycle",summary="【Update】大眾運輸資訊-公共自行車")
async def updateStation(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1.  \n
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證

    collection = await MongoDB.getCollection("traffic_hero", "information_public_bicycle")
    collection_list = await MongoDB.getCollection("traffic_hero", "information_public_bicycle_list")
    collection_availability = await MongoDB.getCollection("traffic_hero", "information_public_bicycle_availability")
    
    await collection.drop() # 刪除所有資料
    
    try:
        # 建立索引
        collection_list.create_index("station_uid")
        collection_availability.create_index("station_uid")
        collection.create_index("station_uid")

        # 取得 information_public_bicycle_list 所有資料
        list_data = list(collection_list.find({}, {"_id": 0}))

        # 取得 information_public_bicycle_availability 所有資料
        availability_data = list(collection_availability.find({}, {"_id": 0}))

        # 將所有 list 資料合併到 information_public_bicycle 中
        bulk_operations = []
        for item in sorted(list_data, key=lambda x: x["station_uid"]):
            station_uid = item["station_uid"]
            # 找尋對應的 availability 資料
            availability_item = next((x for x in availability_data if x["station_uid"] == station_uid), None)

            if availability_item:
                combined_data = OrderedDict([
                    ("area", item["area"]),
                    ("station_uid", station_uid),
                    ("station_id", item["station_id"]),
                    ("station_name_zh_tw", item["station_name_zh_tw"]),
                    ("station_address_zh_tw", item["station_address_zh_tw"]),
                    ("bikes_capacity", item["bikes_capacity"]),
                    ("service_type", item["service_type"]),
                    ("icon_url", item["icon_url"]),
                    ("service_status", availability_item["service_status"]),
                    ("available_rent_bikes", availability_item["available_rent_bikes"]),
                    ("available_return_bikes", availability_item["available_return_bikes"]),
                    ("available_rent_bikes_detail", availability_item["available_rent_bikes_detail"]),
                    ("location", item["location"]),
                    # ("src_update_time", availability_item["src_update_time"]),
                    # ("update_time", availability_item["update_time"])
                ])

                # 加入批量操作
                bulk_operations.append(
                    UpdateOne({"station_uid": station_uid},
                            {"$set": combined_data},
                            upsert=True)
                )

        # 執行批量操作
        collection.bulk_write(bulk_operations)

    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}

    return {"message": f"更新成功，總筆數:{await collection.count_documents({})}"}
        
    
    # 合併以下資料至collection
    # information_public_bicycle_list
    # {
    #   "_id": {
    #     "$oid": "655ca95f3e0032b914ba7e98"
    #   },
    #   "area": "TaipeiCity",
    #   "station_uid": "TPE500101001",
    #   "station_id": "500101001",
    #   "station_name_zh_tw": "捷運科技大樓站",
    #   "station_address_zh_tw": "復興南路二段235號前",
    #   "bikes_capacity": 28,
    #   "service_type": "YouBike2.0",
    #   "icon_url": "https://play-lh.googleusercontent.com/DmDUCLudSKb5hZV5P_i3S-oZkF-udIPfW1OSa-fq2FS9rTV5A2v_tTGgpS0wuSs0bA=w240-h480-rw",
    #   "location": {
    #     "longitude": 121.5436,
    #     "latitude": 25.02605
    #   }
    # }
    
    # information_public_bicycle_availability
    # {
    #     "_id": {
    #         "$oid": "655ca4dd283b830ed8f1fdb8"
    #     },
    #     "station_uid": "TPE500101001",
    #     "station_id": "500101001",
    #     "service_status": "正常營運",
    #     "service_type": "YouBike2.0",
    #     "available_rent_bikes": 10,
    #     "available_return_bikes": 18,
    #     "available_rent_bikes_detail": {
    #         "general_bikes": 10,
    #         "electric_bikes": 0
    #     },
    #     "src_update_time": "2023-11-21T20:37:05+08:00",
    #     "update_time": "2023-11-21T20:38:07+08:00"
    # }
    
    
    
    
    # try:
    #     data = collection_list.find({}, {"_id": 0})
    #     documents = []

    #     for d in data:
    #         availability = collection_availability.find_one({"station_id": d["station_id"]}, {"_id": 0})
    #         documents.append({
    #             "area": d["area"],
    #             "station_uid": d["station_uid"],
    #             "station_id": d["station_id"],
    #             "station_name_zh_tw": d["station_name_zh_tw"],
    #             "station_address_zh_tw": d["station_address_zh_tw"],
    #             "bikes_capacity": d["bikes_capacity"],
    #             "service_type": d["service_type"],
    #             "icon_url": d["icon_url"],
    #             "location":{
    #                 "longitude": d["location"]["longitude"],
    #                 "latitude": d["location"]["latitude"],
    #             },
    #             "available_spaces": availability["AvailableSpaces"],
    #             "available_bikes": availability["AvailableBikes"],
    #             "src_update_time": availability["SrcUpdateTime"],
    #             "update_time": availability["UpdateTime"]
    #         })

    #     await collection.drop()
    #     await collection.insert_many(documents)
        
    # except Exception as e:
    #     return {"message": f"更新失敗，錯誤訊息:{e}"}

    # return {"message": f"更新成功，總筆數:{await collection.count_documents({})}"}
    
