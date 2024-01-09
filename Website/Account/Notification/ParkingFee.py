from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import asyncio
import httpx
import time
import firebase_admin
from firebase_admin import credentials, messaging
from typing import Optional
import Service.Token as Token
from Main import MongoDB  # MongoDB連線實例
import Website.Account.Notification.Broadcast as broadcast

router = APIRouter(tags=["0.會員管理(Website)"], prefix="/Website/Account")

class NotificationData(BaseModel):
    title: str
    body: str

@router.post("/Notification/ParkingFee", summary="【Create】推播通知-路邊停車費")
async def send_parking_fee_notifications(email: Optional[str] = None, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    payload = Token.verifyToken(token.credentials, "user")  # JWT驗證
    user_collection = await MongoDB.getCollection("traffic_hero", "user_data")

    query = {"email": email} if email else {}
    users_cursor = user_collection.find(query, {"_id": 0, "notification_token": 1, "vehicle": 1})

    async for user in users_cursor:
        print(f"處理用戶: {user}")  # 日誌輸出
        for vehicle in user.get("vehicle", []):
            print(f"處理車輛: {vehicle}")  # 日誌輸出
            fee_info = await parkingFee(vehicle["license_plate_number"], vehicle["type"])
            if fee_info:
                for device_token in user.get("notification_token", []):
                    if device_token:
                        title = f"路邊停車費({vehicle['license_plate_number']})"
                        body = f"待繳納金額:${fee_info['total_amount']}\n請至Traffic Hero APP查看詳情"
                        print(f"發送通知: {title} - {body}")  # 日誌輸出
                        broadcast.send(device_token, title, body)

    return {"message": "推播通知已發送"}

async def parkingFee(license_plate_number: str, type: str):
    collection = await MongoDB.getCollection("traffic_hero", "parking_fee")
    task = []
    for result in await collection.find({}, {"_id": 0}).to_list(length=None):
        if result.get("area") != "test":
            url = result.get("url").replace("Insert_CarID", license_plate_number).replace("Insert_CarType", type)
            task.append(asyncio.create_task(processData(result["area"], url)))

    details = await asyncio.gather(*task)
    valid_details = [detail for detail in details if detail and detail["amount"] != 0]

    if not valid_details: # 如果沒有任何一個地區有停車費資料
        return None

    total_amount = sum(detail["amount"] for detail in valid_details if detail["amount"] >= 0)
    return {
        "license_plate_number": license_plate_number,
        "type": codeToText(type),
        "total_amount": total_amount,
        "detail": valid_details
    }

async def processData(area, url):
    collection = await MongoDB.getCollection("traffic_hero", "parking_fee")

    try:
        area_record = await collection.find_one({"area": area})
        if area_record and area_record.get("status"):
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(url)
                if response.status_code == 429:  # Too Many Requests
                    await asyncio.sleep(1)  # 稍作等待再重試
                    response = await client.get(url)  # 重試一次
                dataAll = response.json()

            result = dataAll.get('Result')
            if result:
                bills = result.get('Bills', [])
                reminders = result.get('Reminders', []) if result.get('Reminders') is not None else []
                totalAmount = sum(bill.get('PayAmount', 0) for bill in bills) + \
                              sum(reminder.get('PayAmount', 0) for reminder in reminders)
                return {
                    "area": area,
                    "amount": totalAmount,
                    "bills": bills,
                    "reminders": reminders,
                    "detail": "查詢成功"
                }
            else:
                return {
                    "area": area,
                    "amount": 0,
                    "detail": "無停車費資料"
                }
    except Exception as e:
        return {"area": area, "amount": -1, "detail": "服務維護中"}

def codeToText(code: str):  # 類別轉換
    match code:
        case "C":
            return "汽車"
        case "M":
            return "機車"
        case "O":
            return "其他(如拖車)"
