import telebot
from config import ADMINS, API_TOKEN, START_TEXT
from pytube import YouTube
from tiktok_downloader import ttdownloader
import random
import os
import json
import time
import shutil

def youtube_download(link):
    yt = YouTube(link, use_oauth=True, allow_oauth_cache=True)
    video = yt.streams.get_highest_resolution()
    if (video.filesize > 52428800):
        return 145
    file = video.download(output_path="./downloads/")
    return file

def tiktok_download(link):
    video = ttdownloader(link)
    filepath = f"downloads/{str(random.randint(10000, 99999))}.mp4"
    video[0].download(filepath)
    return filepath

def add_to_users(user_id):
    users = json.load(open("users.json"))
    if (str(user_id)) in users:
        pass
    else:
        usr = {"videos": []}
        users[str(user_id)] = usr
        json.dump(users, open("users.json", "w"))

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=["start"])
def start_cmd(message):
    add_to_users(message.from_user.id)
    bot.reply_to(message, START_TEXT)

@bot.message_handler(commands=["makecopy"])
def makecopy_cmd(message):
    if (message.from_user.id in ADMINS):
        filename = f"users-{str(int(time.time()))}.json"
        shutil.copy2("users.json", f"copies/{filename}")
        bot.reply_to(message, f"Резервная копия сохранена: ```{filename}```", parse_mode="markdown")
        bot.send_document(message.chat.id, open(f"copies/{filename}", "r"))

@bot.message_handler(commands=["sendmsg"])
def sendmsg_cmd(message):
    if (message.from_user.id in ADMINS):
        users = json.load(open("users.json"))
        if (message.reply_to_message):
            msg = message.reply_to_message
            for usr in users.keys():
                bot.send_message(usr, msg.text, parse_mode="html")

@bot.message_handler(content_types=["text"])
def text_handler(message):
    add_to_users(message.from_user.id)
    if "https://" in message.text and len(message.text.split()) == 1:
        success = False
        if "youtu.be" in message.text or "youtube.com/watch/" in message.text or "youtube.com/shorts/" in message.text:
            msg = bot.reply_to(message, "Скачиваю видео...")
            filepath = youtube_download(message.text)
            if (filepath == 145):
                bot.reply_to(message, "Видео весит больше 50МБ, скинь что-нибудь полегче.")
                return None
            bot.delete_message(msg.chat.id, msg.message_id)
            msg = bot.reply_to(message, "Видео скачано, отправляю...")
            bot.send_video(message.chat.id, open(filepath, "rb"), timeout=600)
            bot.delete_message(msg.chat.id, msg.message_id)
            os.remove(filepath)
            success = True
        elif "tiktok.com" in message.text:
            msg = bot.reply_to(message, "Скачиваю видео...")
            filepath = tiktok_download(message.text)
            bot.delete_message(msg.chat.id, msg.message_id)
            msg = bot.reply_to(message, "Видео скачано, отправляю...")
            bot.send_video(message.chat.id, open(filepath, "rb"), timeout=600)
            bot.delete_message(msg.chat.id, msg.message_id)
            os.remove(filepath)
            success = True
        if success:
            users = json.load(open("users.json"))
            users[str(message.from_user.id)]["videos"].append(message.text)
            json.dump(users, open("users.json", "w"))



bot.infinity_polling()
