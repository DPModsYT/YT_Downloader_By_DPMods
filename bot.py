# bot.py

import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import BOT_TOKEN, FORCE_SUB_CHANNEL, ADMIN_USERNAME
from utils.database import add_user, get_users
from utils.downloader import get_formats, download_video

if not os.path.exists("downloads"):
    os.makedirs("downloads")

bot = Client("yt_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

def force_subscribe_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Join Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL}")],
        [InlineKeyboardButton("✅ Joined", callback_data="check_sub")]
    ])

async def check_subscription(bot, message):
    try:
        member = await bot.get_chat_member(f"@{FORCE_SUB_CHANNEL}", message.from_user.id)
        if member.status not in ("member", "administrator", "creator"):
            await message.reply("You must join our channel first.", reply_markup=force_subscribe_keyboard())
            return False
        return True
    except:
        await message.reply("Error checking subscription. Try again later.")
        return False

@bot.on_message(filters.command("start"))
async def start_cmd(bot, message):
    if not await check_subscription(bot, message):
        return
    add_user(message.from_user.id)
    await message.reply(
        "Send any YouTube video or Shorts link and choose MP3 or MP4 format with quality."
    )

@bot.on_message(filters.command("stats"))
async def stats(bot, message):
    if message.from_user.username != ADMIN_USERNAME:
        return
    users = get_users()
    await message.reply(f"Total Users: {len(users)}")

@bot.on_callback_query()
async def handle_callback(bot, callback):
    if callback.data == "check_sub":
        if await check_subscription(bot, callback.message):
            await callback.message.edit("You can now use the bot. Send a YouTube link.")

@bot.on_message(filters.text & ~filters.command(["start", "stats"]))
async def handle_url(bot, message):
    if not await check_subscription(bot, message):
        return
    url = message.text.strip()
    await message.reply("Fetching available formats...")
    try:
        formats = get_formats(url)
    except Exception as e:
        await message.reply("Failed to fetch formats. Invalid URL or video blocked.")
        return

    buttons = []
    for fmt in formats:
        label = f"{fmt['ext']} {fmt['resolution']}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"dl|{url}|{fmt['format_id']}")])

    reply_markup = InlineKeyboardMarkup(buttons[:30])
    await message.reply("Select format:", reply_markup=reply_markup)

@bot.on_callback_query(filters.regex(r"^dl\|"))
async def handle_download(bot, callback):
    _, url, fmt_id = callback.data.split("|")
    await callback.message.edit("Downloading...")
    try:
        file_path, title = download_video(url, fmt_id)
        await bot.send_chat_action(callback.from_user.id, "upload_document")
        await bot.send_document(callback.from_user.id, file_path, caption=title)
        os.remove(file_path)
    except Exception as e:
        await callback.message.edit("Failed to download or send the file.")

bot.run()
