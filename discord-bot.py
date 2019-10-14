import discord
from os import getenv
from discord.ext import commands

import bot_utils
import worker


bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


@bot.command()
async def check_server(ctx, region: str):
    header = bot_utils.quote(region, f_format="glsl")
    data = bot_utils.quote(bot_utils.parse_server(worker.check_server(region, bot=True)))
    await ctx.send(header)
    await ctx.send(data)


@bot.command()
async def check_servers(ctx):
    servers = worker.check_servers(bot=True)
    for region, server in servers.items():
        header = bot_utils.quote(region, f_format="glsl")
        data = bot_utils.quote(bot_utils.parse_server(server))
        if len(data) > 1999:
            print(len((data)))
            print(((data)))
        await ctx.send(header)
        await ctx.send(data)


bot.run(getenv("DISCORD_TOKEN"))
