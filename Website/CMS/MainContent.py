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

@router.get("/Main/Read", summary="【Read】即時訊息推播-主要內容")
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
    
        collection_main_car = await MongoDB.getCollection("traffic_hero","cms_main_car")
        collection_main_scooter = await MongoDB.getCollection("traffic_hero","cms_main_scooter")

        result_car = collection_main_car.find({},{"_id":0})
        result_scooter = collection_main_scooter.find({},{"_id":0})
    
        return {"car": list(result_car), "scooter": list(result_scooter)}

@router.post("/Main/Create", summary="【Create】即時訊息推播-主要內容")
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
    return await create(mode,data)

async def create(mode:str ,data: cms):
        collection_main_car = await MongoDB.getCollection("traffic_hero","cms_main_car")
        collection_main_scooter = await MongoDB.getCollection("traffic_hero","cms_main_scooter")
        
        match mode:
                case "car":
                        inserted_result = collection_main_car.insert_one(data)
                        id = str(inserted_result.inserted_id)
                        collection_main_car.update_one({"_id": inserted_result.inserted_id}, {"$set": {"id": id}})
                case "scooter":
                        inserted_result = collection_main_scooter.insert_one(data)
                        id = str(inserted_result.inserted_id)
                        collection_main_scooter.update_one({"_id": inserted_result.inserted_id}, {"$set": {"id": id}})
                
        return {"message": "新增成功"}

@router.put("/Main/Update", summary="【Update】即時訊息推播-主要內容")
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
        
        collection_main_car = await MongoDB.getCollection("traffic_hero","cms_main_car")
        collection_main_scooter = await MongoDB.getCollection("traffic_hero","cms_main_scooter")
        
        match mode:
                case "car":
                        collection_main_car.update_one({"id": data.id}, {"$set": data.dict()})
                case "scooter":
                        collection_main_scooter.update_one({"id": data.id}, {"$set": data.dict()})

        return {"message": "更新成功"}

@router.delete("/Main/Delete", summary="【Delete】即時訊息推播-主要內容")
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
    
        collection_main_car = await MongoDB.getCollection("traffic_hero","cms_main_car")
        collection_main_scooter = await MongoDB.getCollection("traffic_hero","cms_main_scooter")
    
        match mode:
                case "car":
                        collection_main_car.delete_one({"id": id})
                case "scooter":
                        collection_main_scooter.delete_one({"id": id})

        return {"message": "刪除成功"}