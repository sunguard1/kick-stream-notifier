# kick-stream-notifier

import asyncio
import logging
from pyppeteer import launch
from telegram import Bot

TELEGRAM_BOT_TOKEN = "7880098472:AAHw26Jr-MJ9o9KnttBLzDkkh92EM7LXZRU"
CHAT_ID = "-1002013791533"
STREAMERS = [
    "ynknowme",
    "dokkorkl",
    "gantver1",
    "karssen_tv",
    "evg_67",
    "anarabdullaev",
    "markbulahhh",
    "serpens2025",
    "god-of-alcohol",
    "bolt077",
    "naidimenyakogdaochneshsya"
]
CHECK_INTERVAL = 60  # seconds

logging.basicConfig(level=logging.INFO)

async def get_stream_info(page, username):
    url = f"https://kick.com/{username}"
    await page.goto(url, timeout=60000)
    await page.waitForTimeout(5000)
    content = await page.content()
    is_live = 'LIVE' in content or 'live-indicator' in content
    screenshot_path = f"screenshot_{username}.png"
    await page.screenshot({'path': screenshot_path, 'fullPage': False})
    return is_live, url, screenshot_path

async def check_streamers():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    notified = set()

    while True:
        for username in STREAMERS:
            try:
                is_live, url, screenshot = await get_stream_info(page, username)
                if is_live and username not in notified:
                    await bot.send_photo(
                        chat_id=CHAT_ID,
                        photo=open(screenshot, 'rb'),
                        caption=f"🎥 Стрим начался: [{username}]({url})",
                        parse_mode='Markdown'
                    )
                    notified.add(username)
                    logging.info(f"Notified about {username}")
                elif not is_live and username in notified:
                    notified.remove(username)
            except Exception as e:
                logging.error(f"Error checking {username}: {e}")
        await asyncio.sleep(CHECK_INTERVAL)

async def main():
    logging.info("✅ Бот запущен. Следит за стримерами.")
    await check_streamers()

if __name__ == '__main__':
    asyncio.run(main())