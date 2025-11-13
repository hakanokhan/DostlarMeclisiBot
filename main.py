# main.py — Dostlar Meclisi | Render için Düzeltilmiş Sürüm 🔥
from telethon import TelegramClient, events
from telebot import TeleBot
import asyncio, re, time, threading
from flask import Flask

# --- AYARLAR ---
api_id = 18872089
api_hash = 'e410fe46dd11d639a36f3d2fa03ea901'
BOT_TOKEN = "8249259150:AAHVvFZPXx6YSxh5SntYmPzU_CaLyzMzIEg"

TARGET_GROUP = -1003027355359
ADMIN_ID = 1556304675

allowed_sites = ['maribet', 'palazzobet', 'betpas', 'bahsine']
blocked_sites = ['baywin', 'supertotobet', 'onwin', 'betist', 'betroad']

CODE_TTL = 7200
DELETE_DELAY = 60
SEND_DELAY = 0.5
DUPLICATE_DELAY = 30

# Render için NUMARA SORMAYAN session
user = TelegramClient('session', api_id, api_hash)
bot = TeleBot(BOT_TOKEN)
app = Flask(__name__)

sent_codes = {}
recent_sites = {}

@app.route('/')
def home():
    return "🔥 Dostlar Meclisi Bot Aktif (Render) 🔥"

def already_sent(code):
    now = time.time()
    if code in sent_codes and (now - sent_codes[code]) < CODE_TTL:
        return True
    sent_codes[code] = now
    return False

def site_spam(site):
    now = time.time()
    if site in recent_sites and (now - recent_sites[site]) < DUPLICATE_DELAY:
        return True
    recent_sites[site] = now
    return False

def extract_site_name(link):
    match = re.search(r'https?://(?:www\.)?([a-zA-Z0-9\-]+)', link)
    return match.group(1).upper() if match else "SITE"

# --- GELİŞMİŞ DİNLEYİCİ ---
@user.on(events.NewMessage)
async def listener(event):
    text = (event.raw_text or "").strip()
    if not text:
        return

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) < 3:
        return

    site_line, code_line, link = None, None, None

    for l in lines:
        if not site_line and re.match(r'^[A-Za-z0-9\-]{3,}$', l):
            site_line = l
        elif not code_line and re.match(r'^[A-Za-z0-9]{4,20}$', l):
            code_line = l
        elif not link and "http" in l:
            link = l

    if not (site_line and code_line and link):
        return

    blocked_words = [
        'etkinlik','kampanya','turnuva','yatırım','hediye','bonus',
        'duyuru','reklam','çekiliş','sohbet','katıl','güvenilir',
        'test','deneme','youtube','canlı','yayındayız','stream'
    ]

    if any(w in text.lower() for w in blocked_words):
        return
    if any(s in text.lower() for s in blocked_sites):
        return
    if already_sent(code_line) or site_spam(site_line):
        return

    msg_html = f"<b>{site_line.upper()}</b>\n\n<code>{code_line}</code>\n\n{link}"

    try:
        await asyncio.sleep(SEND_DELAY)
        sent_msg = bot.send_message(TARGET_GROUP, msg_html, parse_mode="HTML")
        print(f"✅ İlk gelen gönderildi: {site_line} - {code_line}")

        await asyncio.sleep(DELETE_DELAY)
        bot.delete_message(TARGET_GROUP, sent_msg.message_id)
        print(f"🗑️ Silindi: {site_line}")

    except Exception as e:
        print("⚠️ Gönderim hatası:", e)

# --- DUYURU ---
@bot.message_handler(commands=['duyuru','acil'])
def handle_announcement(message):
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ Yetkin yok moruq.")
    cmd = message.text.split(' ', 1)
    if len(cmd) < 2:
        return bot.reply_to(message, "⚠️ Mesajı yazmayı unuttun moruq.")
    header = "🔴 <b>ACİL DUYURU</b>" if message.text.startswith("/acil") else "📢 <b>DOSTLAR MECLİSİ DUYURUSU</b>"
    bot.send_message(message.chat.id, f"{header}\n\n{cmd[1]}", parse_mode="HTML")
    bot.reply_to(message, "✅ Duyuru gönderildi moruq.")

# --- TELEBOT POLLING ---
def start_bot_polling():
    print("🤖 TeleBot polling başlıyor...")
    while True:
        try:
            bot.remove_webhook()
            bot.infinity_polling(skip_pending=True, allowed_updates=["message"], timeout=60)
        except Exception as e:
            print("⚠️ Polling koptu, 5 sn sonra tekrar:", e)
            time.sleep(5)

# --- TELETHON START (NUMARA YOK!) ---
async def start_telethon():
    await user.start()  # Artık input yok
    print("🚀 Telethon aktif!")
    await user.run_until_disconnected()

# --- ANA BAŞLATMA ---
if __name__ == "__main__":
    threading.Thread(target=start_bot_polling, daemon=True).start()
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080), daemon=True).start()
    asyncio.run(start_telethon())
