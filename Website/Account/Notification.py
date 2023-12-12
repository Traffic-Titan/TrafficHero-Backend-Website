from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from Service.Token import *
import Function.Time as Time
import Function.VerificationCode as Code
from Main import MongoDB # 引用MongoDB連線實例
import Service.Token as Token
from pyfcm import FCMNotification
import os
from dotenv import load_dotenv

router = APIRouter(tags=["0.會員管理(Website)"],prefix="/Website/Account")

FCM_API_KEY = os.getenv('FCM_API_KEY') # Firebase 金鑰

push_service = FCMNotification(api_key=FCM_API_KEY) # 初始化 FCMNotification

@router.post("/Notification/Broadcast",summary="【Create】新增推播通知並發送(Dev)")
async def broadcast(title: str, body: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    payload = Token.verifyToken(token.credentials,"user") # JWT驗證
    
    collection = await MongoDB.getCollection("traffic_hero","user_data") # 連線MongoDB
    
    # 查詢所有已訂閱的使用者
    subscribers = collection.find({"notification_token": {"$exists": True}}, {"_id": 0, "notification_token": 1})

    # 逐一發送通知給所有訂閱者的所有裝置
    for subscriber in subscribers:
        for device_token in subscriber.get("notification_token", []):
            # 構建推送的訊息
            message = {
                "title": title,
                "body": body,
            }

            # 使用 PyFCM 發送通知
            result = push_service.notify_single_device(registration_id=device_token, data_message=message)

            # 檢查推送結果
            if result["success"] != 1:
                raise HTTPException(status_code=500, detail="Failed to send notification")

    return {"message": "推播通知已發送"}
