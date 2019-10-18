import discord
from os import getenv
from discord.ext import commands
from typing import Optional

import bot_utils
import worker

bot = commands.Bot(command_prefix="!")

kill_list = bot_utils.load_killist()

bot.remove_command("help")


@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


@bot.command()
async def check_server(ctx, region: str, port: Optional[int] = None):
    if region:
        await bot_utils.check_server(ctx, region, port=port)
    else:
        await bot_utils.error(ctx)


@bot.command()
async def check_servers(ctx, port: Optional[int] = None):
    await bot_utils.check_servers(ctx, port=port)


@bot.command()
async def search_player(ctx, *args):
    await bot_utils.search_player(ctx, args)


@bot.command()
async def is_angel(ctx, *args):
    await bot_utils.seek_angels(ctx, args)


@bot.command()
async def check_list(ctx):
    await bot_utils.check_killist(ctx, kill_list)


@bot.command()
async def get_list(ctx):
    await ctx.send(" ".join(list(map(lambda x: f"`{x}`", kill_list))))


@bot.command()
async def add_player(ctx, *args):
    username = " ".join(args)
    if username:
        if username != "Player":
            if username not in kill_list:
                kill_list.append(username)
                bot_utils.save_killist(kill_list)
                await ctx.send(f"{username} is in tracklist now")
            else:
                await ctx.send("he is already in the tracklist")
        else:
            await ctx.send("srysly??")
    else:
        await bot_utils.error(ctx)


@bot.command()
async def help(ctx):
    embed = discord.Embed()

    embed.add_field(name="!check_server REGION [PORT]", value="checks server", inline=False)
    embed.add_field(name="!check_servers [PORT]", value="checks all active servers", inline=False)

    embed.add_field(name="!check_list ", value="check the player list", inline=False)
    embed.add_field(name="!add_player PLAYER_NAME", value="adds the player into the list", inline=False)
    embed.add_field(name="!get_list", value="returns the list", inline=False)

    embed.add_field(name="!search_player PLAYER_NAME", value="checks if the player is online", inline=False)
    embed.add_field(name="!is_angel username", value="idk, just angelic name checker", inline=False)

    embed.add_field(name="!help", value="Gives this message", inline=False)
    await ctx.send(embed=embed)


bot.run(getenv("DISCORD_TOKEN"))
