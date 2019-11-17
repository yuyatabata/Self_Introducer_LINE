import json
import os
from flask import Flask,request,abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, PostbackEvent, TextMessage, TextSendMessage, TemplateSendMessage, ImageSendMessage, CarouselTemplate, ConfirmTemplate, ButtonsTemplate, ImageCarouselTemplate
    , FlexSendMessage, BubbleContainer,CarouselContainer,URIAction
)
app = Flask(__name__)

channel_secret = os.environ["YOUR_CHANNEL_SECRET"]
# os.getenv('channel_secret', default=None)
channel_access_token = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
# os.getenv('channel_access_token', default=None)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# with open("design/profile.json") as f:
#     profile_data = json.load(f)

# with open("design/work.json") as f:
#     work_data = json.load(f)

with open("design/portfolio.json") as f:
    portfolio_data = json.load(f)


@app.route("/health", methods=["GET"])
def healthcheck():
    return "healty!"

@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    # リクエストがLINE Platformから送信されたものであることを確認
    signature = request.headers["X-Line-Signature"]

    # get request body as text：クライアント(LINE)からのリクエストをテキストとして受け取る
    body = request.get_data(as_text=True)
    # DEBUG用のログを出力できます。
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        #署名signatureを検証。通ればhandleに定義されている関数を呼び出す。(handleされたメソッドを呼び出す)＝@handlerのついた関数を呼び出す
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


def make_button_template():
    message_template = TemplateSendMessage(
        alt_text="プロフィール",
        template=ButtonsTemplate(
            text="和歌山県出身\nマーケ/広報/管理部など経験。\n今はラクスでエンジニア",
            title="プロフィール",
            image_size="cover",
            thumbnail_image_url="https://avatars2.githubusercontent.com/u/27131456?s=400&u=e69093e842a16f391ac806240f97f1c92451ff47&v=4",
            actions=[
                URIAction(
                    uri="https://github.com/yuyatabata",
                    label="GitHubアカウント"
                )
            ]
        )
    )
    return message_template

def make_confirm_template():
    message_template = TemplateSendMessage(
        alt_text="キャリア",
        template=ConfirmTemplate(
            text="キャリア",
            title="プロフィール",
            actions=[
                {
                    "type":"message",
                    "label":"エンジニア",
                    "text":"エンジニア"
                },
                {
                    "type":"message",
                    "label":"マーケティング",
                    "text":"マーケティング"
                }
            ]
        )
    )
    return message_template

def make_carousel_flex():
    message_template = FlexSendMessage(
        alt_text = "ポートフォリオ",
        contents = CarouselContainer.new_from_json_dict(portfolio_data)
    )
    return message_template

@handler.add(MessageEvent, message=TextMessage)
def handle_image_message(event):
    text = event.message.text
    if text == "プロフィール":
        messages = make_button_template()
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    if text == "仕事内容":
        messages = make_confirm_template()
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    if text == "エンジニア":
        messages = make_confirm_template()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Pythonによるデータ分析やシステム開発を担当しています。')
        )
    if text == "マーケティング":
        messages = make_confirm_template()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='SEO、LPO、Web広告の運用、事業KPIの設定などやってきました。')
        )
    if text == "ポートフォリオ":
        messages = make_carousel_flex()
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)