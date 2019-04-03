# coding: utf-8

import os, subprocess, shlex, asyncio
from dotenv import load_dotenv

from flask import Flask, request, abort
from linebot import (
  LineBotApi, WebhookHandler
)
from linebot.exceptions import (
  InvalidSignatureError
)
from linebot.models import (
  MessageEvent, TextMessage, LocationMessage, TextSendMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn
)
from src.weather import Weather

load_dotenv()

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/myhomeapi", methods=['POST'])
def myhomeapi():
  signature = request.headers['X-Line-Signature']

  body = request.get_data(as_text=True)
  app.logger.info("Request body: " + body)
  try:
    handler.handle(body, signature)
  except InvalidSignatureError:
    abort(400)

  return 'OK'

def say(msg, symbol=True):
  speed = "100"
  if symbol: #音声記号列での発話の有無(デフォルト:有)
    cmd1 = "AquesTalkPi -s " + speed + " -k \"" + msg + "\""
  else:
    cmd1 = "AquesTalkPi -s " + speed + " \"" + msg + "\""
  cmd2 = "aplay"
  process1=subprocess.Popen(shlex.split(cmd1),stdout=subprocess.PIPE)
  process2=subprocess.Popen(shlex.split(cmd2),stdin=process1.stdout)
  process2.wait()
  #proc = subprocess.call( cmd, shell=True )
  #proc = subprocess.call( cmd .strip().split(" ") )

def aplay(wavfile):
  cmd = "aplay " + wavfile
  proc =  subprocess.call( cmd.strip().split(" ") )

@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
  msg = None
  req = event.message.text

  #リクエスト一覧
  #test
  if req == "a":
    msg = "ok"
  #help1
  elif req == "?" or req == "？":
    msg = "1. 地名の前に!をつけると地名を読み上げます。\n"
    msg += "2. 時間の前に#をつけると時間を読み上げます。"
  #help2
  elif req == "help" or req == "h":
    msg = "request:\n"
    msg += "  gohome: !\n"
    msg += "  time: #\n"
    msg += "  weather: w/wc/wt/wtd\n"
    msg += "  say: (else)"
  #gohome
  elif req[0] == "!" or req[0] == "！":
    msg = "gohome"+"リクエストを受け付けました"
    sentence = "い'まから,/;か'えってきま_ス."
    if req != "!" and req != "！":
      sentence += "ただ'いま、" + req[1:] + "にいま_ス."    
    aplay("res/notice.wav")
    say(sentence)
  #time
  elif req[0] == "#" or req[0] == "＃":
    msg = "time"+"リクエストを受け付けました"
    sentence = "所要時間わ。"+ req[1:] +"です."
    if req != "#" and req[0] != "＃":
      aplay("res/notice.wav")
      say(sentence, False) 
  #weather
  elif req[0] == "w":
    msg = "weather"+"リクエストを受け付けました"
    weather = Weather()
    if req[1] == "c": #current
      dateLabel = "只今"
      condition = weather.showCurrentWeather() #OpenWeatherMap
    elif req[1] == "t": #today
      dateLabel = "今日"
      data = weather.showTodayWeather() #Livedoor Weather Web Service
      condition = data[0]
      if req[2] == "d": #detail
        forecast_text = data[1]
    sentence = dateLabel + "の天気は," + condition + "です."
    if forecast_text != "":
      index = forecast_text.find("【") #【関東甲信地方】以下の情報を切り捨て
      sentence += forecast_text[:index]
    say(sentence, False)
    del weather 
  #say
  else:
    msg = "sayリクエストを受け付けました"
    say(req, False)

  if msg is not None:
      line_bot_api.reply_message(
          event.reply_token,
          TextSendMessage(text=msg)
      )

@handler.add(MessageEvent, message=LocationMessage)
def message_location(event):
  location_name = event.message.title
  msg = "ただいま、" + location_name + "にいます"
  say(msg, False)
  if location_name is not None:
      line_bot_api.reply_message(
          event.reply_token,
          TextSendMessage(text=msg)
      )



if __name__ == "__main__":
  port = int(os.getenv("PORT", 8000))
  app.run(host="0.0.0.0", port=port, debug=True)
