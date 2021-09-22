#!/usr/bin/python3
#coding: utf8

import discord
import youtube_dl
import os
from googleapiclient.discovery import build

youtube = build('youtube', 'v3', developerKey=os.environ.get('YOUTUBE_TOKEN'))
# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Voice(object):
    def __init__(self, bot):
        self.bot = bot
        self.client = None
        if not discord.opus.is_loaded():
            discord.opus.load_opus("libopus.so")
    
    def search(self, text):
        response = youtube.search().list(q=text, part='id,snippet', maxResults=1).execute()
        for result in response.get('items', []):
            return "https://www.youtube.com/watch?v=%s" % result['id']['videoId']
        return None

    async def youtube(self, ctx, URL):
        if self.client is None or not self.client.is_connected():
            for channel in ctx.channel.guild.voice_channels:
                if channel.id == int(os.environ.get('VOICE_CHANNEL')):
                    self.client = await channel.connect()
                    break
        player = await YTDLSource.from_url(URL, loop=self.bot.loop)
        await self.stop()
        self.client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    async def stop(self, *_, **__):
        if self.client is None or not self.client.is_connected():
            return
        self.client.stop()