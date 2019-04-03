# coding: utf-8

import os, subprocess, shlex, asyncio
import math, re
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
from src import weather

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
    msg += "  say: (else)"
  #gohome
  elif req[0] == "!" or req[0] == "！":
    msg = "gohome"+"リクエストを受け付けました"
    sentence1 = "い'まから,/;か'えってきま_ス."
    sentence2 = "ただ'いま、" + req[1:] + "にいま_ス."    
    aplay("res/notice.wav")
    say(sentence1)
    if req != "!" and req != "！":
      say(sentence2)
  #time
  elif req[0] == "#" or req[0] == "＃":
    msg = "time"+"リクエストを受け付けました"
    sentence = "所要時間わ。"+ req[1:] +"です."
    if req != "#" and req[0] != "＃":
      aplay("res/notice.wav")
      say(sentence, False) 
  #whether
  elif req == "w" or req == "nw":
    msg = "weather"+"リクエストを受け付けました"
    data = weather.showCurrentWeather()
    condition = data["forecasts"][0]["telop"]
    '''
    condition_en = data["weather"][0]["main"]
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
    '''
    sentence = "今日の天気は," + condition + "です."
    print(sentence)
    #say(sentence, False)
    
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
