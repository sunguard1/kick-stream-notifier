import asyncio
import logging
from datetime import datetime
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.types import InputFile
from playwright.async_api import async_playwright

BOT_TOKEN = "7880098472:AAHw26Jr-MJ9o9KnttBLzDkkh92EM7LXZRU"
CHAT_ID = -1002066244086
STREAMERS = ["xqc", "nickmercs", "adinross"]
CHECK_INTERVAL = 60

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
active_streams = set()
Path("screenshots").mkdir(exist_ok=True)

async def is_stream_live(page, username):
    url = f"https://kick.com/{username}"
    try:
        await page.goto(url, timeout=30000)
        await page.wait_for_selector("video", timeout=5000)
        return True
    except:
        return False

async def take_screenshot(page, username):
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    path = f"screenshots/{username}_{ts}.png"
    await page.screenshot(path=path, full_page=True)
    return path

async def check_streams():
    logging.info("🔍 Checking streams...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for u in STREAMERS:
            live = await is_stream_live(page, u)
            if live and u not in active_streams:
                path = await take_screenshot(page, u)
                txt = f"🚨 Стрим начался: https://kick.com/{u}"
                await bot.send_photo(chat_id=CHAT_ID, photo=InputFile(path), caption=txt)
                active_streams.add(u)
            elif not live:
                active_streams.discard(u)
        await browser.close()

async def scheduler():
    while True:
        try:
            await check_streams()
        except Exception as e:
            logging.error(f"Error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.send_message(chat_id=CHAT_ID, text=f"✅ Бот запущен. Следит за {len(STREAMERS)} стримерами.")
    await scheduler()

if __name__ == "__main__":
    asyncio.run(main())