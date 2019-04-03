import os, requests
import json
import logging
from dotenv import load_dotenv


def showCurrentWeather():
  load_dotenv()

  #location = "Tokyo"
  #API_key = os.environ["OWM_API_Key"]
  #api = "http://api.openweathermap.org/data/2.5/weather?units=metric&q={city}&APPID={key}"
  location = 130010
  api = "http://weather.livedoor.com/forecast/webservice/json/v1?city={city}"

  #url = api.format(city = location, key = API_key)
  url = api.format(city = location)
  response = requests.get(url)
  data = response.json()
  logging.info("%s", data)
  
  return data
