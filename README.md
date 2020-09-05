# MyHomeRaspberryPi
**Raspberry Pi Server at home.**

![](https://github.com/sakupo/MyHomeRaspberryPi/blob/images/img/MyHomeRSPi.png?raw=true)

Slack または LINE clientをインターフェースとして，家のRaspberryPiに繋がるスピーカーを操作し，
家にいる人に音声でメッセージを伝えます．

このリポジトリでは，RaspberryPiでスピーカーを遠隔操作するサンプルプログラムを示しています．

- OS: Debian 9.8 (stretch)
- 言語: Python 3.7.0
- API: Slack API/LINE Messaging API
- FrameWork: FastAPI(Slack)/Flask(Line)
- 音声合成: AquestalkPi

Slack用サーバーの起動(myhomeディレクトリ)
```bash
> uvicorn myhome:app --port [ポート番号] --host 0.0.0.0
```

Line用サーバーの起動(myhomeディレクトリ)
```bash
> python myhome_line.py
```
