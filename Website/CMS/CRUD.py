from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from selenium import webdriver
import time
from PIL import Image
import os
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(tags=["3.即時訊息推播(Website)"],prefix="/Website/CMS")

class cms(BaseModel):
    type: str
    icon: str
    main_content: list[list[list[str]]]
    main_color: list[list[list[str]]]
    sidebar_content: list[str]
    sidebar_color: list[str]
    voice: str
    longitude: float
    latitude: float
    direction: str
    distance: float
    piority: int
    start: datetime
    end: datetime
    id: str = None

collection_car = MongoDB.getCollection("traffic_hero","cms_car")
collection_scooter = MongoDB.getCollection("traffic_hero","cms_scooter")

@router.get("/Read", summary="【Read】即時訊息推播-推播內容")
async def getContent(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    result_car = collection_car.find({},{"_id":0})
    result_scooter = collection_scooter.find({},{"_id":0})
    
    return {"car": list(result_car), "scooter": list(result_scooter)}

@router.post("/Create", summary="【Create】即時訊息推播-推播內容")
async def createContentAPI(mode:str ,data: cms, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    return createContent(mode,data)

def createContent(mode:str ,data: cms):
    match mode:
        case "car":
            inserted_result = collection_car.insert_one(data)
            id = str(inserted_result.inserted_id)
            collection_car.update_one({"_id": inserted_result.inserted_id}, {"$set": {"id": id}})
        case "scooter":
            inserted_result = collection_scooter.insert_one(data)
            id = str(inserted_result.inserted_id)
            collection_scooter.update_one({"_id": inserted_result.inserted_id}, {"$set": {"id": id}})
            
    return {"message": "新增成功"}

@router.put("/Update", summary="【Update】即時訊息推播-推播內容")
async def updateContent(mode:str ,data: cms, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    match mode:
        case "car":
            collection_car.update_one({"id": data.id}, {"$set": data.dict()})
        case "scooter":
            collection_scooter.update_one({"id": data.id}, {"$set": data.dict()})

    return {"message": "更新成功"}

@router.delete("/Delete", summary="【Delete】即時訊息推播-推播內容")
async def deleteContent(mode:str , id: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. 
    二、Input \n
            1. 
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    
    match mode:
        case "car":
            collection_car.delete_one({"id": id})
        case "scooter":
            collection_scooter.delete_one({"id": id})

    return {"message": "刪除成功"}