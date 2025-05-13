
import json
import time
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

TOKEN = os.getenv("8093648591:AAGGh-Mdzo9W15AxR2xwgKJ0SJg62kdtmiY")
ADMIN_ID = os.getenv("6991944640")
DATA_FILE = 'data.json'
CLICK_REWARD = 10
REF_BONUS = 25
WITHDRAW_LIMIT = 500
CLICK_DELAY = 10

try:
    with open(DATA_FILE, 'r') as f:
        users = json.load(f)
except:
    users = {}

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f)

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    uid = str(user.id)
    if uid not in users:
        users[uid] = {"name": user.first_name, "points": 0, "last_click": 0, "ref_by": None, "wallet": ""}
        if context.args:
            ref = context.args[0]
            if ref != uid and ref in users:
                users[uid]['ref_by'] = ref
                users[ref]['points'] += REF_BONUS
    save_data()
    update.message.reply_text(f"أهلا {user.first_name}!
اكتب /earn للتكبيس
/balance لرؤية الرصيد
/setwallet لإدخال محفظتك
/withdraw للسحب
/referral لرابط الإحالة")

def earn(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    now = time.time()
    if now - users[uid]["last_click"] >= CLICK_DELAY:
        users[uid]["points"] += CLICK_REWARD
        users[uid]["last_click"] = now
        save_data()
        update.message.reply_text(f"كسبت {CLICK_REWARD} نقطة! رصيدك: {users[uid]['points']}")
    else:
        wait = int(CLICK_DELAY - (now - users[uid]["last_click"]))
        update.message.reply_text(f"انتظر {wait} ثانية قبل الضغط مرة أخرى.")

def balance(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    update.message.reply_text(f"رصيدك: {users[uid]['points']} نقطة.")

def setwallet(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    if context.args:
        users[uid]['wallet'] = context.args[0]
        save_data()
        update.message.reply_text("تم حفظ محفظتك.")
    else:
        update.message.reply_text("أرسل الأمر هكذا:
/setwallet YOUR_BEP20_ADDRESS")

def withdraw(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    if users[uid]['points'] >= WITHDRAW_LIMIT:
        if users[uid]['wallet']:
            msg = f"سحب جديد:
اسم: {users[uid]['name']}
ID: {uid}
نقاط: {users[uid]['points']}
محفظة: {users[uid]['wallet']}"
            context.bot.send_message(chat_id=ADMIN_ID, text=msg)
            update.message.reply_text("تم إرسال طلب السحب.")
        else:
            update.message.reply_text("أدخل محفظتك أولا بـ /setwallet")
    else:
        update.message.reply_text(f"يجب أن يكون لديك {WITHDRAW_LIMIT} نقطة على الأقل.")

def referral(update: Update, context: CallbackContext):
    uid = str(update.effective_user.id)
    link = f"https://t.me/USDTxxClickBot?start={uid}"
    update.message.reply_text(f"رابط الإحالة:
{link}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("earn", earn))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("setwallet", setwallet))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("referral", referral))
    app.run_polling()
