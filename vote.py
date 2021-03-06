#!/usr/bin/python3
#coding: utf8

import os
import redis
from discord.ext import commands

class Vote(object):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        @bot.command()
        @commands.dm_only()
        async def token(ctx: commands.Context, token: str):
            r = redis.Redis(host='redis')
            r.set('TOKEN_'+str(ctx.message.author.id), token)
            await ctx.send('Token enregistrΓ© ! π')

        @bot.event
        async def on_raw_reaction_add(payload):
            if payload.channel_id != int(os.environ.get('VOTE_CHANNEL_ID')):
                return
            channel = await bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            file_id = message.content.split('/')[-1]
            r = redis.Redis(host='redis')
            token = r.get('TOKEN_'+str(payload.member.id))
            if token is None:
                return
            token = token.decode('utf-8')
            if payload.name == 'π' or payload.name == 'π':
                pass # TODO implement vote
            elif payload.name == 'β' or payload.name == 'β':
                pass # TODO implement selection

        @bot.event
        async def on_raw_reaction_delete(payload):
            if payload.channel_id != int(os.environ.get('VOTE_CHANNEL_ID')):
                return
            channel = await bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            file_id = message.content.split('/')[-1]
            r = redis.Redis(host='redis')
            token = r.get('TOKEN_'+str(payload.member.id)).decode('utf-8')
            if token is None:
                return
            token = token.decode('utf-8')
            if payload.name == 'π' or payload.name == 'π':
                pass # TODO implement vote

        @bot.event
        async def on_message(message):
            await bot.process_commands(message)
            if message.channel.id != int(os.environ.get('VOTE_CHANNEL_ID')):
                return
            await message.add_reaction('π')
            await message.add_reaction('π')
            await message.add_reaction('β')
            await message.add_reaction('β')
