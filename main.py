import os
import json
import re
from typing import Dict

import discord
from discord.ext import commands
from dotenv import load_dotenv


def load_settings() -> Dict[str, Dict[str, str]]:
    with open("settings.json", "r") as f:
        return json.load(f)


def is_valid_room_number(message: str) -> bool:
    return bool(re.match(r"^\d{5}$", message))


def get_new_channel_name(settings: Dict[str, str], room_num: str) -> str:
    channel_name_fmt = settings["channel_name_fmt"]
    return channel_name_fmt.format(room_num=room_num)


load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
SETTINGS = load_settings()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("------")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    guild_id = str(message.guild.id)
    if guild_id not in SETTINGS:
        return

    guild_settings = SETTINGS[guild_id]
    text_channel_ids = guild_settings["text_channel_ids"]

    if str(message.channel.id) not in text_channel_ids:
        return

    if is_valid_room_number(message.content):
        room_num = message.content
        voice_channel_id = int(guild_settings["voice_channel_id"])
        new_channel_name = get_new_channel_name(guild_settings, room_num)

        voice_channel = bot.get_channel(voice_channel_id)
        await voice_channel.edit(name=new_channel_name)


bot.run(TOKEN)
