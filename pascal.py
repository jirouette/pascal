#!/usr/bin/python3
#coding: utf8

import os
import time
import discord
from discord.ext import commands
from voice import Voice

WEBHOOKS = dict()
TEMP_BANLIST = dict()

class Pascal(commands.Bot):
    async def on_ready(self):
        print('Now connected as {0.user.name}'.format(self))
        print('Ready. ')

async def ban(ctx, author):
    await ctx.send("<:ban:792391057706975272>")
    TEMP_BANLIST[author.id] = time.time()

async def is_in_voice_channel(ctx):
    if not voice.client:
        return True
    if ctx.author.id in [member.id for member in voice.client.channel.members]:
        return True
    await ban(ctx, ctx.author)
    return False

async def is_coming_from_text_channel(ctx):
    if ctx.channel.id == int(os.environ.get('TEXT_CHANNEL')):
        return True
    if not ctx.guild:
        await ctx.send('🤫')
    return False

async def is_not_banned(ctx):
    ban_duration = int(os.environ.get('TEMP_BAN_DURATION', 300))
    print("banlist",TEMP_BANLIST)
    if TEMP_BANLIST.get(ctx.author.id, 0) >= (time.time()-ban_duration):
        await ctx.send("<:ban:792391057706975272>")
        return False
    banned_role = int(os.environ.get('BANNED_ROLE'))
    if banned_role in [role.id for role in ctx.author.roles]:
        await ctx.send("<:ban:792391057706975272>")
        return False
    return True

if __name__ == '__main__':
    print("Starting Pascal...")
    bot = Pascal(command_prefix="!")
    voice = Voice(bot)

    @bot.command()
    @commands.check(is_coming_from_text_channel)
    @commands.check(is_in_voice_channel)
    @commands.check(is_not_banned)
    async def music(ctx, *args):
        text = " ".join(args)
        print(text)
        if (text.startswith("https://www.youtube.com/") or
           text.startswith("https://youtube.com/") or
           text.startswith("http://www.youtube.com/") or
           text.startswith("http://youtube.com/") or
           text.startswith("https://youtu.be/") or
           text.startswith("http://youtu.be/")):
            await voice.youtube(ctx, text)
            return await ctx.send('🎵')
        URL = voice.search(text)
        if URL:
            await voice.youtube(ctx, URL)
            return await ctx.send('🎵 '+URL)
        return await ctx.send('😔')
    
    bot.run(os.environ.get('DISCORD_TOKEN'))
