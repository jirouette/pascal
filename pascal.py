#!/usr/bin/python3
#coding: utf8

import os
from discord.ext import commands
from voice import Voice

class Pascal(commands.Bot):
    async def on_ready(self):
        print('Now connected as {0.user.name}'.format(self))
        print('Ready. ')

    async def on_command_error(self, ctx, error):
        pass

if __name__ == '__main__':
    print("Starting Pascal...")
    bot = Pascal(command_prefix="!")
    voice = Voice(bot)
    bot.run(os.environ.get('DISCORD_TOKEN'))
