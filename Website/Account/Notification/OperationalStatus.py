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

@router.post("/Notification/OperationalStatus", summary="【Create】大眾運輸-營運狀態推播通知")
async def broadcast_operational_status(email: Optional[str] = None, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    Token.verifyToken(token.credentials, "user")  # JWT驗證
    user_collection = await MongoDB.getCollection("traffic_hero", "user_data")
    status_collection = await MongoDB.getCollection("traffic_hero", "operational_status")

    # 獲取所有營運狀態
    statuses = status_collection.find({})

    # 查詢所有已訂閱的使用者
    query = {"notification_token": {"$exists": True}}
    if email is not None and email.strip() != "":
        query["email"] = email
    subscribers_cursor = user_collection.find(query, {"_id": 0, "notification_token": 1})

    subscribers = [subscriber async for subscriber in subscribers_cursor]

    if not subscribers:
        raise HTTPException(status_code=404, detail="No subscribers found.")

    async for status in statuses:
        # 只有在狀態不是「正常營運」和「無資料」時才發送通知
        if status['status_text'] not in ["正常營運", "無資料"]:
            title = f"大眾運輸營運狀況"
            body = f"{status['name']} - {status['status_text']}"
            
            for subscriber in subscribers:
                for device_token in subscriber.get("notification_token", []):
                    broadcast.send(device_token, title, body)

    return {"message": "推播通知已發送"}


