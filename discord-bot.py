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
    if region in bot_utils.REGIONS_LIST:
        if not port:
            for port in worker.KNOWN_PORTS:
                port, data = worker.check_server(region, port=port, bot=True)
                await bot_utils.send_server(ctx, f"{region} {port}", data)
        else:
            port, data = worker.check_server(region, port=port, bot=True)
            await bot_utils.send_server(ctx, f"{region} {port}", data)
    else:
        await ctx.send(f"hey, hey. check the region please {bot_utils.REGIONS_STRING}")


@bot.command()
async def check_servers(ctx, port: Optional[int] = None):
    if not port:
        for port in worker.KNOWN_PORTS:
            await bot_utils.check_servers(ctx, port)
    else:
        await bot_utils.check_servers(ctx, port)


@bot.command()
async def search_player(ctx, *args):
    username = " ".join(args)
    if username != "Player":
        _data = worker.search_player(username, bot=True)  # heroku neden walrnus desteklemiyorsun mk
        if _data:
            await ctx.send("ya ya, he is online lets go kill him")
            header, server = _data
            await bot_utils.send_server(ctx, header, server)
        else:
            await ctx.send("no he is not online :(")
    else:
        await ctx.send("srysly??")


bot.run(getenv("DISCORD_TOKEN"))
