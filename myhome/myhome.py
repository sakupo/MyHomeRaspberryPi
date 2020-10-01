# coding: utf-8
import uvicorn
import os, subprocess, shlex, asyncio, json
from dotenv import load_dotenv
from src.aquestalk_util import romajiToKana
import threading

from fastapi import FastAPI
from starlette.requests import Request
import requests
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

load_dotenv()
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SPEAKER_CHANNEL_TOKEN = os.environ["SLACK_SPEAKER_CHANNEL_TOKEN"]

APP_HOME_VIEW = {
                "type": "home",
                "blocks": [
                  {
                    "type": "section",
                    "text": {
                      "type": "mrkdwn",
                      "text": "ようこそ！ここはHomeSpeakerのApp Homeです．"
                    }
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "section",
                    "text": {
                      "type": "mrkdwn",
                      "text": "*使用可能なコマンド*"
                    }
                  },
                  {
                    "type": "section",
                    "text": {
                      "type": "mrkdwn",
                      "text": "`/say [メッセージ]`: メッセージを伝えるとき"
                    }
                  },
                  {
                    "type": "section",
                    "text": {
                      "type": "mrkdwn",
                      "text": "`/go [地名]`: 家に帰るとき"
                    }
                  }
                ]
              }

app = FastAPI()
print("Start server...")

class SlackCommand(BaseModel):
  token: str
  team_id: str
  team_domain: str
  channel_id: str
  channel_name: str
  user_id: str
  user_name: str
  command: str
  text: str
  response_url: str
  trigger_id: str
  api_app_id: str

# post response to Slack App Home
def viewsPublish(user: str, view):
  url = "https://slack.com/api/views.publish"
  payload = {"token": SLACK_BOT_TOKEN, "user_id": user, "view": view}
  headers = {"Content-type": "application/json; charset=UTF-8", "Authorization": "Bearer " + SLACK_BOT_TOKEN}
  r = requests.post(url, data=json.dumps(payload), headers=headers)

# post response to Slack channel
def postSpeakerChannel(message: str):
  url = SLACK_SPEAKER_CHANNEL_TOKEN
  payload = {"text": message}
  r = requests.post(url, data=json.dumps(payload))

def makePostText(cmdName: str):
  return cmdName + "リクエストを受け付けました"

# speaker
def say(msg, symbol=True):
  speed = "100"
  if symbol: #音声記号列での発話の有無(デフォルト:有)
    cmd1 = "AquesTalkPi -s " + speed + " -k \"" + msg + "\""
  else:
    cmd1 = "AquesTalkPi -s " + speed + " \"" + msg + "\""
  cmd2 = "aplay -D plughw:1,0"
  process1=subprocess.Popen(shlex.split(cmd1),stdout=subprocess.PIPE)
  process2=subprocess.Popen(shlex.split(cmd2),stdin=process1.stdout)
  process2.wait()

def aplay(wavfile):
  cmd = "aplay -D plughw:1,0 " + wavfile
  proc =  subprocess.call( cmd.strip().split(" ") )

# gohome
def sayGohome(userName: str, location: str):
  sentence1 = "い'まから,/;" + romajiToKana(userName) + "さんがか'えってきま_ス."
  sentence2 = "ただ'いま、" + location + "にいま_ス."    
  aplay("res/notice.wav")
  say(sentence1)
  if len(location) > 0:
    say(sentence2)

def makeGohomeText(userName: str, location: str):
  message = f"いまからかえります"
  if len(location) > 0:
    message += f" @{location}"
  message += f" from {userName}"
  return message

# say
def saySomething(userName: str, message: str):
  sentence  = romajiToKana(userName) + "さん,からのめっせーじです."
  sentence += message
  aplay("res/notice.wav")
  say(sentence, False)

def makeSayText(userName: str, text: str):
  message = f"{userName}さんからのメッセージ:\n"
  message += text
  return message

# post request
@app.post("/myhome/api/v1/gohome",
          status_code=200)
async def gohome_cmd(req: Request):
  body = await req.form()
  cmd = SlackCommand(**body)
  postThread = threading.Thread(target=postSpeakerChannel(makeGohomeText(cmd.user_name, cmd.text)))
  sayThread  = threading.Thread(target=sayGohome(cmd.user_name, cmd.text))
  postThread.start()
  sayThread.start()
  return {"text": makePostText("gohome")}

@app.post("/myhome/api/v1/say",
          status_code=200)
async def say_cmd(req: Request):
  body = await req.form()
  cmd = SlackCommand(**body)
  postThread = threading.Thread(target=postSpeakerChannel(makeSayText(cmd.user_name, cmd.text)))
  sayThread  = threading.Thread(target=saySomething(cmd.user_name, cmd.text))
  postThread.start()
  sayThread.start()
  return {"text": makePostText("say")}

@app.post("/myhome/api/v1/apphome",
          status_code=200)
async def get_apphome(req: Request):
  body = await req.json()
  type = body["type"] 
  if type == "url_verification":
    return {"challenge": body["challenge"]}
  if type == "event_callback":
    event = body["event"]
    if (event["type"] == "app_home_opened"):
      viewsPublish(event["user"], APP_HOME_VIEW)

@app.post("/myhome/api/v1/actions",
          status_code=200)
async def actions(req: Request):
  body = await req.form()
  print(body["payload"])
  patload = body["payload"] 

"""
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=13241)
"""
