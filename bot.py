import telebot
from config import ADMINS, API_TOKEN, START_TEXT
from pytube import YouTube
from tiktok_downloader import ttdownloader
import random
import os

def youtube_download(link):
    yt = YouTube(link)
    video = yt.streams.get_highest_resolution()
    file = video.download(output_path="./downloads/")
    return file

def tiktok_download(link):
    video = ttdownloader(link)
    filepath = f"downloads/{str(random.randint(10000, 99999))}.mp4"
    video[0].download(filepath)
    return filepath

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=["start"])
def start_cmd(message):
    bot.reply_to(message, START_TEXT)

@bot.message_handler(content_types=["text"])
def text_handler(message):
    if "https://" in message.text and len(message.text.split()) == 1:
        if "youtu.be" in message.text or "youtube.com/watch/" in message.text or "youtube.com/shorts/" in message.text:
            msg = bot.reply_to(message, "Скачиваю видео...")
            filepath = youtube_download(message.text)
            bot.delete_message(msg.chat.id, msg.message_id)
            msg = bot.reply_to(message, "Видео скачано, отправляю...")
            bot.send_video(message.chat.id, open(filepath, "rb"), timeout=600)
            bot.delete_message(msg.chat.id, msg.message_id)
            os.remove(filepath)
            return None
        elif "tiktok.com" in message.text:
            msg = bot.reply_to(message, "Скачиваю видео...")
            filepath = tiktok_download(message.text)
            bot.delete_message(msg.chat.id, msg.message_id)
            msg = bot.reply_to(message, "Видео скачано, отправляю...")
            bot.send_video(message.chat.id, open(filepath, "rb"), timeout=600)
            bot.delete_message(msg.chat.id, msg.message_id)
            os.remove(filepath)

bot.infinity_polling()
