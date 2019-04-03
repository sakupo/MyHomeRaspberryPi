import os, requests
import json, re
import logging
from dotenv import load_dotenv

class Weather:
  def showTodayWeather(self):
    location = 130010
    api = "http://weather.livedoor.com/forecast/webservice/json/v1?city={city}"
    url = api.format(city = location)
    response = requests.get(url)
    data = response.json()
    logging.info("%s", data)

    condition = data["forecasts"][0]["telop"]
    text = data["description"]["text"]
    
    return condition, text

  def showCurrentWeather(self):
    load_dotenv()

    location = "Tokyo"
    API_key = os.environ["OWM_API_Key"]
    api = "http://api.openweathermap.org/data/2.5/weather?units=metric&q={city}&APPID={key}"

    url = api.format(city = location, key = API_key)
    response = requests.get(url)
    data = response.json()
    logging.info("%s", data)

    condition_en = data["weather"][0]["main"]
    #英日対応リスト
    cond_list = (
      ("Thunderstorm",  "雷"),
      ("Drizzle", "弱い雨"),
      ("Rain", "雨"),
      ("Snow", "雪"),
      ("Clear", "晴れ"),
      ("Clouds", "曇り"),
      ("Mist", "霧"),("Smoke", "煙"),("Haze", "薄い霧"),
      ("Dust", "塵"),("Fog", "濃い霧"),("Sand", "砂"),
      ("Ash", "灰"),("Squall", "豪雨"),("Tornado", "竜巻")
    )
    #パターンマッチ
    condition = (lambda cond: next(val for key,val in cond_list if re.match(key, cond)))(condition_en)
    
    return condition
