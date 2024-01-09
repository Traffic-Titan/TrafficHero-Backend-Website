from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from Service.Token import *
import Function.Time as Time
import Function.VerificationCode as Code
from Main import MongoDB # 引用MongoDB連線實例
import Service.Token as Token
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, messaging
from typing import Optional

router = APIRouter(tags=["0.會員管理(Website)"],prefix="/Website/Account")

class NotificationData(BaseModel):
    title: str
    body: str

@router.post("/Notification/Broadcast/All",summary="【Create】新增推播通知並發送")
async def broadcast(title: str, body: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證
    collection = await MongoDB.getCollection("traffic_hero", "user_data")

    # 查詢所有已訂閱的使用者
    cursor = collection.find({"notification_token": {"$exists": True}}, {"_id": 0, "notification_token": 1})
    
    async for subscriber in cursor:
        for device_token in subscriber.get("notification_token", []):
            send(device_token, title, body)

    return {"message": "推播通知已發送"}

class UserFilter(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    vehicle: Optional[str] = None

@router.post("/Notification/Broadcast/Specific", summary="【Create】針對特定使用者推播通知")
async def broadcast_specific(filter: UserFilter, title: str, body: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials,"user") # JWT驗證

    query = {"notification_token": {"$exists": True}}
    if filter.email:
        query["email"] = filter.email
    if filter.role:
        query["role"] = filter.role
    if filter.vehicle:
        query["vehicle.license_plate_number"] = filter.vehicle

    collection = await MongoDB.getCollection("traffic_hero", "user_data")
    cursor = collection.find(query, {"_id": 0, "notification_token": 1})

    # 逐一發送通知給符合條件的訂閱者
    async for subscriber in cursor:
        for device_token in subscriber.get("notification_token", []):
            send(device_token, title, body)

    return {"message": "推播通知已發送"}

def send(device_token, title, body):
    if not isinstance(device_token, str) or not device_token.strip():
        return  # 跳過無效或空的設備Token

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=device_token,
    )

    try:
        response = messaging.send(message)
    except firebase_admin.exceptions.FirebaseError as e:
        if 'Requested entity was not found' in str(e):
            return  # 跳過無效的設備Token
        else:
            raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

