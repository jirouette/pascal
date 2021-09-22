#!/usr/bin/python3
#coding: utf8

import os
import discord
from discord.ext import commands
from voice import Voice

WEBHOOKS = dict()

class Pascal(commands.Bot):
    async def on_ready(self):
        print('Now connected as {0.user.name}'.format(self))
        print('Ready. ')

if __name__ == '__main__':
    print("Starting Pascal...")
    bot = Pascal(command_prefix="!")
    voice = Voice(bot)

    @bot.command()
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
            print("selected URL",URL)
            await voice.youtube(ctx, URL)
            return await ctx.send('🎵')
        return await ctx.send('😔')
    
    bot.run(os.environ.get('DISCORD_TOKEN'))
