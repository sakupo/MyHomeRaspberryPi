# coding: utf-8
import uvicorn
import os, subprocess, shlex, asyncio, json
from dotenv import load_dotenv
import threading

from fastapi import FastAPI
from starlette.requests import Request
import requests
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

load_dotenv()
SLACK_SPEAKER_CHANNEL_TOKEN = os.environ["SLACK_SPEAKER_CHANNEL_TOKEN"]

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
def sayGohome(location: str):
  sentence1 = "い'まから,/;か'えってきま_ス."
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
def saySomething(sentence: str):
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
  sayThread  = threading.Thread(target=sayGohome(cmd.text))
  postThread.start()
  sayThread.start()
  return {"text": makePostText("gohome")}

@app.post("/myhome/api/v1/say",
          status_code=200)
async def say_cmd(req: Request):
  body = await req.form()
  cmd = SlackCommand(**body)
  postThread = threading.Thread(target=postSpeakerChannel(makeSayText(cmd.user_name, cmd.text)))
  sayThread  = threading.Thread(target=saySomething(cmd.text))
  postThread.start()
  sayThread.start()
  return {"text": makePostText("say")}

"""
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=13241)
"""
