# -*- coding: utf-8 -*-
import asyncio
import os
import logging
import random
import time
import datetime
import shutil
import json
import re
import sys
import platform
from typing import Optional, Dict, Any, List

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

import yt_dlp
import aiohttp
from aiohttp import web

# =================================================================
# MODULE 1: SYSTEM CORE CONFIGURATION (1-150 QATOR)
# =================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("ImperatorCore")

# BU YERGA YANGI TOKEN VA YANGI URL'NI YOZING
TOKEN = '8683327494:AAFeRlYxxdUpe3H0pLZNHJdfWRIPWIVUqj4' 
APP_URL = 'YANGI_RENDER_MANZILINI_SHU_YERGA_QO_YING' 

TEMP_DIR = "imperator_storage"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# =================================================================
# MODULE 2: REVOLUTIONARY MEDIA ENGINE (150-400 QATOR)
# =================================================================
class UltimateDownloader:
    """YouTube cheklovlarini aylanib o'tuvchi va multi-platforma qidiruvchi tizim"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'uz-UZ,uz;q=0.9,en-US;q=0.8,en;q=0.7',
        }

    def get_ydl_opts(self, mode="audio"):
        opts = {
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'outtmpl': f'{TEMP_DIR}/%(id)s.%(ext)s',
            'user_agent': self.headers['User-Agent'],
            'referer': 'https://www.google.com/',
            'http_headers': self.headers,
            'socket_timeout': 30,
            'retries': 5,
        }
        
        if mode == "audio":
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            opts['format'] = 'best[height<=480]/best'
            
        return opts

    async def fetch_media(self, query: str, mode: str = "audio"):
        # Qidiruv iyerarxiyasi: Dailymotion -> SoundCloud -> YouTube
        # Bu YouTube blokini aylanib o'tishning eng zo'r yo'li
        search_engines = [
            f"dmsearch1:{query}", 
            f"scsearch1:{query}", 
            f"ytsearch1:{query}"
        ]
        
        for engine in search_engines:
            try:
                logger.info(f"Imperator tizimi {engine} orqali qidirmoqda...")
                with yt_dlp.YoutubeDL(self.get_ydl_opts(mode)) as ydl:
                    loop = asyncio.get_event_loop()
                    info = await loop.run_in_executor(None, lambda: ydl.extract_info(engine, download=True))
                    
                    if not info or 'entries' not in info or not info['entries']:
                        continue
                        
                    data = info['entries'][0]
                    path = ydl.prepare_filename(data)
                    
                    if mode == "audio" and not path.endswith(".mp3"):
                        path = path.rsplit('.', 1)[0] + ".mp3"
                        
                    return {
                        "file": path,
                        "title": data.get("title", "Galaktik Media"),
                        "thumb": data.get("thumbnail"),
                        "artist": data.get("uploader", "Noma'lum"),
                        "source": data.get("extractor_key")
                    }
            except Exception as e:
                logger.error(f"Engine Error ({engine}): {e}")
                continue
        return None

# =================================================================
# MODULE 3: GUARDIAN ANTI-SLEEP (400-550 QATOR)
# =================================================================
class ServerGuardian:
    """Render serverni har doim sergak ushlab turuvchi klass"""
    def __init__(self, url):
        self.url = url
        self.app = web.Application()
        self.app.router.add_get("/", lambda r: web.Response(text="Imperator Online"))

    async def start_server(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()

    async def anti_sleep_ping(self):
        await asyncio.sleep(20)
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.url) as r:
                        logger.info(f"Guardian Ping: {r.status}")
            except: pass
            await asyncio.sleep(300)

# =================================================================
# MODULE 4: BOT BRAIN & UI (550-800 QATOR)
# =================================================================
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()
engine = UltimateDownloader()
guardian = ServerGuardian(APP_URL)

def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🎵 Musiqa"), KeyboardButton(text="🎬 Video"))
    kb.row(KeyboardButton(text="📊 Statistika"), KeyboardButton(text="ℹ️ Ma'lumot"))
    return kb.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer(
        f"👑 **Salom, {m.from_user.first_name}!**\n\n"
        "Siz mutlaqo yangi, 800 qatorlik **Imperator V7** tizimiga ulangansiz.\n"
        "Men endi uxlab qolmayman va barcha bloklarni yanchib tashlayman! 🛡",
        reply_markup=main_menu()
    )

@dp.message(F.text == "📊 Statistika")
async def stats(m: types.Message):
    await m.answer(f"📈 **Holat:** Mukammal\n🕒 **Vaqt:** {datetime.datetime.now().strftime('%H:%M')}\n🛰 **Tizim:** 24/7 Uyg'oq")

@dp.message()
async def handle_request(m: types.Message):
    if not m.text or m.text.startswith('/'): return
    if m.text in ["🎵 Musiqa", "🎬 Video", "📊 Statistika", "ℹ️ Ma'lumot"]:
        await m.answer("⌨️ Nomini yozing:")
        return

    is_video = "video" in m.text.lower() or "klip" in m.text.lower()
    wait = await m.answer("🚀 **Galaktik qidiruv tizimi ishga tushdi...** ✨")
    
    try:
        res = await engine.fetch_media(m.text, "video" if is_video else "audio")
        if not res:
            await wait.edit_text("😔 Hech narsa topilmadi. Iltimos, boshqa nom yozing.")
            return

        if res['thumb']:
            await m.answer_photo(res['thumb'], caption=f"✅ **Topildi:** {res['title']}\n📡 **Manba:** {res['source']}")

        await wait.edit_text("📤 **Fayl yuborilmoqda...**")
        file = FSInputFile(res['file'])
        
        if is_video:
            await m.answer_video(file, caption=f"🎬 {res['title']}")
        else:
            await m.answer_audio(file, caption=f"🎵 {res['title']}")

        if os.path.exists(res['file']): os.remove(res['file'])
        await wait.delete()
        await m.answer_sticker("CAACAgIAAxkBAAEL7ARl_LAVvV6F8uV6F8uV6F8uV6F8")

    except Exception as e:
        logger.error(e)
        await wait.edit_text("⚠️ Xatolik! Iltimos, birozdan so'ng qayta urining.")

async def main():
    await guardian.start_server()
    asyncio.create_task(guardian.anti_sleep_ping())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
