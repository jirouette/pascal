#!/usr/bin/python3
#coding: utf8

import discord
import asyncio
import os
import feedparser
import redis
from dateutil import parser
from discord.ext import commands


class Rss(object):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_rss_and_send())

    async def check_rss_and_send(self):
        channel = discord.Webhook.from_url(os.environ.get('RSS_WEBHOOK'), adapter=discord.RequestsWebhookAdapter())
        while True:
            news_feed = feedparser.parse(os.environ.get('RSS_URL'))
            r = redis.Redis(host='redis')
            last_entry_pub_date = parser.parse(r.get('LAST_ENTRY').decode('utf-8'))
            pub_date = None
            for entry in news_feed.entries:
                if pub_date is None:
                    pub_date = entry.published
                if last_entry_pub_date >= parser.parse(entry.published):
                    break
                channel.send(entry.link, username=os.environ.get("RSS_USERNAME"), avatar_url=os.environ.get("RSS_AVATAR_URL"))
            r.set('LAST_ENTRY', pub_date)
            await asyncio.sleep(60)
