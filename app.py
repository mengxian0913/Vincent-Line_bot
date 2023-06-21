from config import line_bot_api, handler

from sent_messege import *
from setting import *

from detect import (
    DETECT_NEWS,
    CODEFORCES_CLASS,
    DETECT_OBJECTS
)

from auto_register_codeforces_contest import (
    REGISTER_CODEFORCES_CONTEST
)

from speech import getspeech
from meow import meow

from flask import (
    Flask,
    request, 
    abort,
    render_template,
    url_for
)
from linebot import (
    LineBotApi,
    WebhookHandler
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage, 
    TextSendMessage,
    FollowEvent,
    events
)

import time
import threading
from copy import deepcopy
import requests
from bs4 import BeautifulSoup as bs

############################################################

# Linebot setting

app = Flask(__name__)
friend_list = ["f22e1f29a5914bf5899bbff1f81431fb"]
group_list = []
reply_text = ""

DETECT = threading.Thread(target=DETECT_NEWS)
DETECT_START = 0
#######################################################

# All of the function
function_list = [meow, getspeech]


# linebot app
#######################################################

@app.route("/", methods=['GET'])
def home():
    return "Hello, World!"


@app.route("/callback", methods=['POST'])
def callback():
    global DETECT_START
    if DETECT_START == 0:
        DETECT.start()
        DETECT_START = 1

    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


keywords = [["."], ["演講", "speech"]]
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global CODEFORCES_CLASS, form_url
    reply_token_copy = (event.reply_token)
    text = event.message.text.lower()
    current_user_id = event.source.user_id

    if Users.get(current_user_id) == None:
        form_url = request.host_url + 'form'
        messege = f"請填寫個人信息啟動 meowmeow bot!:    {form_url}"
        sentmessege(reply_token_copy, messege + "\n 底下是你的 user id! \n(p.s.你的個資小心保管!!)")
        line_bot_api.push_message(current_user_id, TextSendMessage(text=current_user_id))
        return
    
    elif Users[current_user_id].user_name == None:
        form_url = request.host_url + 'form'
        messege = f"請填寫個人信息啟動 meowmeow bot!:    {form_url}"
        sentmessege(reply_token_copy, messege + "\n 底下是你的 user id! \n(p.s.你的個資小心保管!!)")
        line_bot_api.push_message(current_user_id, TextSendMessage(text=current_user_id))
        return

    if CODEFORCES_CLASS.ASK_STATE == 1:
        CODEFORCES_CLASS.ASK_STATE = 0
        if text == '1' or text == 'yes':
            print("go to register")
            crawler_thread = threading.Thread(target=REGISTER_CODEFORCES_CONTEST, args=(reply_token_copy, Users[current_user_id].codeforces_handle, Users[current_user_id].codeforces_password))
            crawler_thread.start()
            return
        
    now_event = 0
    for i in range(0, len(keywords)):
        for word in keywords[i]:
            if text == word:
             now_event = i
             break
        if now_event != 0:
            break

    crawler_thread = threading.Thread(target=function_list[now_event], args=(reply_token_copy,))
    crawler_thread.start()

    return



@handler.add(event=events.FollowEvent)
def handle_follow(event):
    print("new member join")
    global form_url
    form_url = request.host_url + 'form'
    user_id = event.source.user_id
    Users[user_id] = User(None, None, None, None, None, None)
    message = "歡迎加入Meowmeow Line Bot！請填寫表單提供信息完成設定！"
    line_bot_api.push_message(user_id, TextSendMessage(text=message + "\n" + form_url + "\n 底下是你的 user id! \n(p.s.你的個資小心保管!!)"))
    line_bot_api.push_message(user_id, TextSendMessage(text=user_id))
    return "please setting the required information to start the function!"


@app.route('/form', methods=['GET', 'POST'])
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    print("Success to submit the form!")
    user_id = request.form.get('user_id')
    name = request.form.get('username')
    email = request.form.get('email')
    nid_account = request.form.get('NID_Account')
    nid_password = request.form.get('NID_Password')
    codeforces_handle = request.form.get('Codeforces_Handle')
    codeforces_password = request.form.get('Codeforces_Password')
    Users[user_id] = (User(user_id, name, email, nid_account, nid_password, codeforces_handle, codeforces_password))

    line_bot_api.push_message(
        user_id,
        TextSendMessage(text="恭喜你成功啟動 MEOW MEOW BOT !!")
    )

    line_bot_api.push_message(
        user_id,
        TextSendMessage(text=DETECT_OBJECTS.IECS_NEWS)
    )

    line_bot_api.push_message(
        user_id,
        TextSendMessage(text=DETECT_OBJECTS.CODEFORCES_CONTEST_NEWS)
    )

    CODEFORCES_CLASS.ASK_STATE = 1

    return "表单提交成功！"


if __name__ == "__main__":
    app.debug = True
    app.run(port=5001)