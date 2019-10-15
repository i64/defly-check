import discord
from os import getenv
from discord.ext import commands
from typing import Optional

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
async def check_server(ctx, region: str, port: Optional[int] = None):
    region = region.upper()
    port, data = worker.check_server(region, port=port, bot=True)

    data_table = bot_utils.quote(bot_utils.parse_server(data))
    header = bot_utils.quote(f"{region} {port}", f_format="glsl")
    await ctx.send(header)
    await ctx.send(data_table)


@bot.command()
async def check_servers(ctx):
    for uri, server in worker._gen_check_servers(bot=True):
        header = bot_utils.quote(bot_utils.region_with_port(uri), f_format="glsl")
        data = bot_utils.quote(bot_utils.parse_server(server))
        if len(data) > 1999:
            print(len((data)))
            print(((data)))
        await ctx.send(header)
        await ctx.send(data)

# @bot.command()
# async def search_player(ctx):

bot.run(getenv("DISCORD_TOKEN"))
