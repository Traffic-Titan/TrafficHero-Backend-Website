from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import Service.Token as Token
from selenium import webdriver
import time
from PIL import Image
import os
from Main import MongoDB # 引用MongoDB連線實例
import Service.TDX as TDX
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List, Union

router = APIRouter(tags=["3.即時訊息推播(Website)"],prefix="/Website/CMS")

class ContentItem(BaseModel):
    text: List[str]
    color: List[str]

class StartEndItem(BaseModel):
    date: datetime

class Location(BaseModel):
    longitude: float
    latitude: float
    direction: str

class cms(BaseModel):
    type: str
    icon: HttpUrl
    content: List[ContentItem]
    voice: str
    location: Location
    distance: float
    priority: int
    start: StartEndItem
    end: StartEndItem
    active: bool
    id: str = None

collection_sidebar_car = MongoDB.getCollection("traffic_hero","cms_sidebar_car")
collection_sidebar_scooter = MongoDB.getCollection("traffic_hero","cms_sidebar_scooter")

@router.get("/Sidebar/Read", summary="【Read】即時訊息推播-側邊欄")
async def get(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
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
    result_car = collection_sidebar_car.find({},{"_id":0})
    result_scooter = collection_sidebar_scooter.find({},{"_id":0})
    
    return {"car": list(result_car), "scooter": list(result_scooter)}

@router.post("/Sidebar/Create", summary="【Create】即時訊息推播-側邊欄")
async def createAPI(mode:str ,data: cms, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
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
    return create(mode,data)

def create(mode:str ,data: cms):
    match mode:
        case "car":
            inserted_result = collection_sidebar_car.insert_one(data)
            id = str(inserted_result.inserted_id)
            collection_sidebar_car.update_one({"_id": inserted_result.inserted_id}, {"$set": {"id": id}})
        case "scooter":
            inserted_result = collection_sidebar_scooter.insert_one(data)
            id = str(inserted_result.inserted_id)
            collection_sidebar_scooter.update_one({"_id": inserted_result.inserted_id}, {"$set": {"id": id}})
            
    return {"message": "新增成功"}

@router.put("/Sidebar/Update", summary="【Update】即時訊息推播-側邊欄")
async def update(mode:str ,data: cms, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
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
            collection_sidebar_car.update_one({"id": data.id}, {"$set": data.dict()})
        case "scooter":
            collection_sidebar_scooter.update_one({"id": data.id}, {"$set": data.dict()})

    return {"message": "更新成功"}

@router.delete("/Sidebar/Delete", summary="【Delete】即時訊息推播-側邊欄")
async def delete(mode:str , id: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
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
            collection_sidebar_car.delete_one({"id": id})
        case "scooter":
            collection_sidebar_scooter.delete_one({"id": id})

    return {"message": "刪除成功"}