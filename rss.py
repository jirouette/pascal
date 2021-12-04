#!/usr/bin/python3
#coding: utf8

import discord
import time
import asyncio
import os
import feedparser
from datetime import datetime
from discord.ext import commands


class Rss(object):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_rss_and_send())
    
    async def check_rss_and_send(self):
        channel = discord.Webhook.from_url(os.environ.get('RSS_WEBHOOK'), adapter=discord.RequestsWebhookAdapter())
        while True:
            news_feed = feedparser.parse(os.environ.get('RSS_URL'))
            with open(os.environ.get('RSS_LAST_ENTRY_FILENAME')) as f:
                guid = f.read()
            first_guid = None
            for entry in news_feed.entries:
                if first_guid is None:
                    first_guid = entry.guid
                if guid == entry.guid:
                    break
                channel.send(entry.link, username=os.environ.get("RSS_USERNAME"), avatar_url=os.environ.get("RSS_AVATAR_URL"))
            with open(os.environ.get('RSS_LAST_ENTRY_FILENAME'), 'w') as f:
                f.write(first_guid)
            await asyncio.sleep(60)
