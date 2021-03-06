#!/usr/bin/python3
#coding: utf8

import discord
import time
import asyncio
import os
from datetime import datetime
from discord.ext import commands


class Temp(object):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_and_delete())

    async def check_and_delete(self):
        channel = await self.bot.fetch_channel(int(os.environ.get('TEMP_CHANNEL')))
        max_seconds = int(os.environ.get('MAX_TEMP_MESSAGE_DURATION'))
        while True:
            pins = await channel.pins()
            async for message in channel.history(oldest_first=True, limit=300):
                if message.id in [msg.id for msg in pins]:
                    continue
                if datetime.timestamp(message.created_at) < (time.time()-max_seconds):
                    await message.delete()
            await asyncio.sleep(60)
