#!/usr/bin/python3
#coding: utf8

import discord
import youtube_dl
import time
import typing
import os
from discord.ext import commands
from googleapiclient.discovery import build

TEMP_BANLIST = dict()
ADMIN_ROLE = int(os.environ.get('ADMIN_ROLE'))

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
    async def from_url(cls, url: str, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Voice(object):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = None
        self.blocked = False
        if not discord.opus.is_loaded():
            discord.opus.load_opus("libopus.so")
        bot.voice = self
        init(bot)
    
    def block(self) -> None:
        self.blocked = True

    def unblock(self) -> None:
        self.blocked = False

    def is_blocked(self) -> bool:
        return self.blocked

    def search(self, text: str) -> typing.Optional[str]:
        response = youtube.search().list(q=text, part='id,snippet', maxResults=1).execute()
        for result in response.get('items', []):
            return "https://www.youtube.com/watch?v=%s" % result['id']['videoId']
        return None

    async def youtube(self, ctx: commands.Context, URL: str) -> None:
        if self.client is None or not self.client.is_connected():
            for channel in ctx.channel.guild.voice_channels:
                if channel.id == int(os.environ.get('VOICE_CHANNEL')):
                    self.client = await channel.connect()
                    break
        player = await YTDLSource.from_url(URL, loop=self.bot.loop)
        await self.stop()
        self.client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    async def stop(self, *_, **__) -> None:
        if self.client is None or not self.client.is_connected():
            return
        self.client.stop()

async def add_ban(ctx: commands.Context, author: discord.Member, duration = -1) -> None:
    if duration < 0:
        duration = int(os.environ.get('TEMP_BAN_DURATION', 300))
    TEMP_BANLIST[author.id] = time.time()+duration

async def is_in_voice_channel(ctx: commands.Context) -> bool:
    if not ctx.bot.voice.client:
        return True
    if ctx.author.id in [member.id for member in ctx.bot.voice.client.channel.members]:
        return True
    await add_ban(ctx, ctx.author)
    await ctx.send("<:ban:792391057706975272>")
    return False

async def is_coming_from_text_channel(ctx: commands.Context) -> bool:
    if ctx.channel.id == int(os.environ.get('TEXT_CHANNEL')):
        return True
    if not ctx.guild:
        await ctx.send('🤫')
    return False

async def is_not_banned(ctx: commands.Context) -> bool:
    if TEMP_BANLIST.get(ctx.author.id, 0) >= time.time():
        await ctx.send("<:ban:792391057706975272>")
        return False
    banned_role = int(os.environ.get('BANNED_ROLE'))
    if banned_role in [role.id for role in ctx.author.roles]:
        await ctx.send("<:ban:792391057706975272>")
        return False
    return True

async def is_not_blocked(ctx: commands.Context) -> bool:
    if ctx.bot.voice.is_blocked():
        await ctx.send('❌')
        return False
    return True

def init(bot: commands.Bot) -> None:
    @bot.command()
    @commands.check(is_coming_from_text_channel)
    @commands.check(is_in_voice_channel)
    @commands.check(is_not_banned)
    @commands.check(is_not_blocked)
    async def music(ctx: commands.Context, *args) -> None:
        text = " ".join(args)
        print(text)
        if (text.startswith("https://www.youtube.com/") or
           text.startswith("https://youtube.com/") or
           text.startswith("http://www.youtube.com/") or
           text.startswith("http://youtube.com/") or
           text.startswith("https://youtu.be/") or
           text.startswith("http://youtu.be/")):
            await ctx.bot.voice.youtube(ctx, text)
            return await ctx.send('🎵')
        URL = ctx.bot.voice.search(text)
        if URL:
            await ctx.bot.voice.youtube(ctx, URL)
            return await ctx.send('🎵 '+URL)
        await ctx.send('😔')

    @bot.command()
    @commands.check(is_coming_from_text_channel)
    @commands.has_role(ADMIN_ROLE)
    async def unban(ctx: commands.Context, member: typing.Optional[discord.Member]) -> None:
        if not member:
            TEMP_BANLIST.clear()
        else:
            del TEMP_BANLIST[member.id]
        await ctx.send('👌')

    @bot.command()
    @commands.check(is_coming_from_text_channel)
    @commands.has_role(ADMIN_ROLE)
    async def ban(ctx: commands.Context, member: discord.Member, duration: typing.Optional[int] = -1) -> None:
        await add_ban(ctx, member, duration*60)
        await ctx.send('🔨')

    @bot.command()
    @commands.check(is_coming_from_text_channel)
    @commands.has_role(ADMIN_ROLE)
    async def block(ctx: commands.Context) -> None:
        ctx.bot.voice.block()
        await ctx.send('👌')

    @bot.command()
    @commands.check(is_coming_from_text_channel)
    @commands.has_role(ADMIN_ROLE)
    async def unblock(ctx: commands.Context) -> None:
        ctx.bot.voice.unblock()
        await ctx.send('👌')