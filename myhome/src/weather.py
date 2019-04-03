import os, requests
import json
from dotenv import load_dotenv


def showCurrentWeather():
  load_dotenv()

  location = "Tokyo"
  API_key = os.environ["OWM_API_Key"]
  api = "http://api.openweathermap.org/data/2.5/weather?units=metric&q={city}&APPID={key}"

  url = api.format(city = location, key = API_key)
  response = requests.get(url)
  data = response.json()
  jsonText = json.dumps(data, indent=4)
  print(jsonText)