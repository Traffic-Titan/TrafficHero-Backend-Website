"""
尚未整理完畢
"""
from bs4 import BeautifulSoup
import urllib.request
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from Main import MongoDB # 引用MongoDB連線實例
import Function.Time as Time
import Service.Token as Token
import Function.Logo as Logo

router = APIRouter(tags=["2.最新消息(Website)"],prefix="/Website/News")

@router.put("/PublicBicycle",summary="【Update】最新消息-公共自行車")
async def updateNewsAPI(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    一、資料來源: \n
            1. YouBike微笑單車 - 最新消息 - 站點公告
                https://www.youbike.com.tw/region/main/news/status/ \n
    二、Input \n
            1. 縣市列表：臺北市、新北市、桃園市、新竹縣、新竹市、新竹科學園區、苗栗縣、台中市、嘉義市、臺南市、高雄市、屏東縣
    三、Output \n
            1. 
    四、說明 \n
            1.
    """
    Token.verifyToken(token.credentials,"admin") # JWT驗證
    return await updateNews()

async def updateNews():  
    collection = await MongoDB.getCollection("traffic_hero","news_public_bicycle")
     
    try:
        # Initial
        context = {}
        context_return = []

        # BeautifulSoup4
        response = urllib.request.urlopen('https://www.youbike.com.tw/region/main/news/status/')
        soup = BeautifulSoup(response.read().decode('utf-8'),'html.parser')
        countryAbbreviationList = {"臺北市":"taipei","新北市":"ntpc","桃園市":"tycg","新竹縣":"hsinchu","新竹市":"hccg","新竹科學園區":"sipa","苗栗縣":"miaoli","臺中市":"i","嘉義市":"chiayi","臺南市":"tainan","高雄市":"kcg","屏東縣":"pthg"}
        # 定位Select標籤
        selectList = soup.find('select',id='h-select-area')
        optionList = selectList.find_all('option')
        for city, area in countryAbbreviationList.items():
            url = f'https://www.youbike.com.tw/region/{area}/news/status/'
            response = urllib.request.urlopen(url)
            soup = BeautifulSoup(response.read().decode('utf-8'),'html.parser')
            city_data = await processData(area,soup)
            context_return.extend(city_data)

        await collection.drop() # 刪除該collection所有資料
        await collection.insert_many(context_return)
    except Exception as e:
        return {"message": f"更新失敗，錯誤訊息:{e}"}

    return {"message": f"更新成功，總筆數:{await collection.count_documents({})}"}

async def processData(area, soup): # 尚未完成縣市分類
    #  Initial
    title_array = []
    url_array = []
    publicTime_array = []
    documents = []


    # Title處理
    all_title = soup.find_all('span',class_="news-list-type")
    for title in all_title:
        title_array.append(title.text)

    # publicTime處理
    all_publicTime = soup.find_all('span',class_="news-list-date")
    for time in all_publicTime:
        publicTime_array.append(time.text)

        # url處理，url是 class:news-list-date 的父類
        url = time.findParent('a')
        url_array.append(url.get('href'))
        
    logo_url = await Logo.get("public_bicycle", "All") # 取得Logo
    
    for data in range(0,len(all_title)):
        match area:
            case "taipei":
                area = "TaipeiCity"
            case "ntpc":
                area = "NewTaipeiCity"
            case "tycg":
                area = "TaoyuanCity"
            case "hsinchu":
                area = "HsinchuCounty"
            case "hccg":
                area = "HsinchuCity"
            case "sipa":
                area = "HsinchuCity"
            case "miaoli":
                area = "MiaoliCounty"
            case "i":
                area = "TaichungCity"
            case "chiayi":
                area = "ChiayiCity"
            case "tainan":
                area = "TainanCity"
            case "kcg":
                area = "KaohsiungCity"
            case "pthg":
                area = "PingtungCounty"
            case _:
                area = area
        
        document = {
            "area": area,
            "title": title_array[data],
            "news_category": "站點公告",
            "update_time": publicTime_array[data],
            "news_url": url_array[data],
            "logo_url": logo_url
        }
        documents.append(document)
    return documents