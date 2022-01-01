#!/usr/bin/python3
#coding: utf8

import asyncio
import os
import random

class Radio(object):
    def __init__(self, voice):
        self.playlist = []
        self.voice = voice
        self.voice.bot.loop.create_task(self.get_last_500_youtube_links())
        self.voice.bot.loop.create_task(self.insert_radio())

    async def get_last_500_youtube_links(self):
        channel = await self.voice.bot.fetch_channel(int(os.environ.get('MUSIC_CHANNEL_ID')))
        while True:
            self.playlist = []
            async for message in channel.history(limit=10000):
                for word in message.content.split():
                    if (word.startswith("https://www.youtube.com/") or
                        word.startswith("https://youtube.com/") or
                        word.startswith("http://www.youtube.com/") or
                        word.startswith("http://youtube.com/") or
                        word.startswith("https://youtu.be/") or
                        word.startswith("http://youtu.be/")):
                        self.playlist.append(word)
                        if len(self.playlist) == 500:
                            break
                if len(self.playlist) == 500:
                    break
            print("Renewed radio playlist")
            await asyncio.sleep(60*60*24)

    async def insert_radio(self):
        await asyncio.sleep(20)
        channel = await self.voice.bot.fetch_channel(int(os.environ.get('TEXT_CHANNEL')))
        while True:
            await asyncio.sleep(10)
            if self.voice.queue or not self.playlist:
                continue
            URL = random.choice(self.playlist)
            await channel.send('🔀🎵 '+URL)
            try:
                await self.voice.youtube(None, URL)
            except:
                continue
