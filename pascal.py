#!/usr/bin/python3
#coding: utf8

import os
from discord.ext import commands
from voice import Voice
from temp import Temp
from rss import Rss
from vote import Vote
from radio import Radio

class Pascal(commands.Bot):
    async def on_ready(self):
        print('Now connected as {0.user.name}'.format(self))
        voice = Voice(bot)
        print("Initialized Voice")
        temp = Temp(bot)
        print("Initialized Temp")
        rss = Rss(bot)
        print("Initialized RSS")
        vote = Vote(bot)
        print("Initialized Vote.")
        radio = Radio(voice)
        print("Initialized Radio.")
        print('Ready. ')

    async def on_command_error(self, ctx, error):
        pass

if __name__ == '__main__':
    print("Starting Pascal...")
    bot = Pascal(command_prefix="!")
    bot.run(os.environ.get('DISCORD_TOKEN'))
