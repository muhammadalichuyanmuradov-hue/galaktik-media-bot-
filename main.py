import os, asyncio, datetime, logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, BotCommand
import yt_dlp
import aiohttp

# --- KONFIGURATSIYA ---
TOKEN = "8683327494:AAFeRlYxxdUpe3H0pLZNHJdfWRIPWIVUqj4"
APP_URL = "https://galaktik-media-bot.onrender.com" # Masalan: https://galaktik-media-bot.onrender.com

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- KLAVIATURA ---
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎵 Musiqa"), KeyboardButton(text="🎬 Video")],
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="ℹ️ Ma'lumot")]
    ],
    resize_keyboard=True
)

# --- MEDIA YUKLOVCHI ---
class ImperatorEngine:
    def __init__(self):
        self.path = "downloads"
        if not os.path.exists(self.path): os.makedirs(self.path)

    async def download(self, query, is_video=False):
        # Ayyorlik: Audio uchun Soundcloud, Video uchun YouTube qidiruvini majburlaymiz
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]' if is_video else 'bestaudio/best',
            'outtmpl': f'{self.path}/%(id)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'default_search': 'ytsearch' if is_video else 'scsearch', 
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, query, download=True)
                if 'entries' in info: info = info['entries'][0]
                return {
                    'file': ydl.prepare_filename(info),
                    'title': info.get('title', 'Noma\'lum'),
                    'source': "YouTube" if is_video else "Soundcloud"
                }
        except Exception as e:
            logging.error(f"Xato: {e}")
            return None

engine = ImperatorEngine()

# --- ANTI-SLEEP (UYQUGA QARSHI) ---
async def keep_alive():
    """Serverni har 10 daqiqada uyg'otib turadi"""
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(APP_URL) as response:
                    logging.info(f"Anti-Sleep: Server uyg'oq {response.status}")
        except: pass
        await asyncio.sleep(600) # 10 daqiqa

# --- BUYRUQLAR ---
@dp.message(Command("start"))
async def start(m: types.Message):
    # Tanishuv va tashqi ko'rinish
    await m.answer_sticker("CAACAgIAAxkBAAEL_") # Stiker ID
    await m.answer(
        f"🌟 **Assalomu alaykum, {m.from_user.first_name}!**\n\n"
        "Men sizning professional media yordamchingizman. 🤖\n\n"
        "🎬 **Video** — YouTube'dan (Eng yaxshi sifat).\n"
        "🎵 **Musiqa** — Soundcloud va boshqalardan.\n\n"
        "Marhamat, quyidagi tugmalardan foydalaning!",
        reply_markup=menu
    )

@dp.message(Command("video"))
async def v_cmd(m: types.Message):
    await m.answer("🎬 **Video qidirish rejimi.**\nNomini yoki YouTube linkini yuboring:")

@dp.message(Command("musiqa"))
async def m_cmd(m: types.Message):
    await m.answer("🎵 **Musiqa qidirish rejimi.**\nNomini yoki Soundcloud linkini yuboring:")

# --- ASOSIY MANTIQ ---
@dp.message()
async def main_handler(m: types.Message):
    if not m.text or m.text.startswith('/'): return
    
    if m.text == "📊 Statistika":
        await m.answer(f"📈 **Holat:** Online\n🕒 **Vaqt:** {datetime.datetime.now().strftime('%H:%M')}\n🛰 **Tizim:** 24/7 Uyg'oq")
        return
    elif m.text == "ℹ️ Ma'lumot":
        await m.answer("🤖 **Imperator AI v10.0**\nMedia yuklash bo'yicha eng aqlli tizim.")
        return

    # Video yoki Musiqa ekanligini aniqlash
    is_video = any(x in m.text.lower() for x in ['video', 'klip', 'clip', 'mp4', 'kino']) or m.text == "🎬 Video"
    
    if m.text in ["🎵 Musiqa", "🎬 Video"]:
        await m.answer(f"Tushunarli! Endi {m.text} nomini yozing:")
        return

    wait = await m.answer("🔍 **Galaktik qidiruv ketmoqda...**")
    res = await engine.download(m.text, is_video)

    if not res:
        await wait.edit_text("❌ Kechirasiz, hech narsa topilmadi. Boshqa nom yozing.")
        return

    await wait.edit_text("📤 **Fayl yuborilmoqda...**")
    file = FSInputFile(res['file'])
    
    try:
        if is_video:
            await m.answer_video(file, caption=f"🎬 {res['title']}\n📡 Manba: YouTube")
        else:
            await m.answer_audio(file, caption=f"🎵 {res['title']}\n📡 Manba: Soundcloud")
        
        await m.answer("😊 Raxmat! Xizmatingizga tayyorman ✨")
    except Exception as e:
        await m.answer("⚠️ Fayl yuborishda xatolik (Hajmi 50MB dan kattadir).")
    finally:
        if os.path.exists(res['file']): os.remove(res['file'])
        await wait.delete()

# --- ISHGA TUSHIRISH ---
async def main():
    # Uyquga qarshi vazifa
    asyncio.create_task(keep_alive())
    
    # Chap burchak menyusi
    await bot.set_my_commands([
        BotCommand(command="start", description="Botni yangilash"),
        BotCommand(command="video", description="Video yuklash"),
        BotCommand(command="musiqa", description="Musiqa yuklash")
    ])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
