import discord
from discord.ext import commands

import bot_utils

from os import getenv
from functools import lru_cache

from typing import Optional, List, Generator

bot = commands.Bot(command_prefix="!")
bot.remove_command("help")

tracklist = bot_utils.load_tracklist()
loglist = bot_utils.load_loglist()


MAX_LEN = 2000 - 8

@lru_cache
def serialize_list() -> List[str]:
    data = list(_chunk_users(tracklist))
    return data


def _chunk_users(track_list: List[str]) -> Generator[str, None, None]:
    ser = lambda l: f"```\n{', '.join(l)}\n```"
    result = []
    _len = 0
    _done = True
    for user in track_list:
        if MAX_LEN > (_len:=(_len + len(user) + 2)):
            _done = False
            result.append(user)
        else:
            _len = len(user)
            _done = True
            yield ser(result)
            result = [user]
    
    if not _done:
        yield ser(result) 

# print(serialize_list())
# __import__('sys').exit(0)

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")


@bot.command()
async def check_server(
    ctx: commands.Context, region: str, port: Optional[int] = None
) -> None:
    if __debug__:
        bot_utils.logger(ctx, bot_utils.Logger.CHECK_SERVER)

    if region:
        await bot_utils.check_server(ctx, region, port=port)
    else:
        await bot_utils.error(ctx)


@bot.command()
async def check_servers(ctx: commands.Context, port: Optional[str] = None) -> None:
    if __debug__:
        bot_utils.logger(ctx, bot_utils.Logger.CHECK_SERVERS)

    await bot_utils.check_servers(ctx, port=port)


@bot.command()
async def get_link(
    ctx: commands.Context, region: str, port: Optional[str] = None
) -> None:
    if __debug__:
        bot_utils.logger(ctx, bot_utils.Logger.GET_LINK)

    await ctx.send(bot_utils.get_link(region=region, port=port))


@bot.command()
async def search_player(ctx: commands.Context, *args) -> None:
    if __debug__:
        bot_utils.logger(ctx, bot_utils.Logger.SEARCH_PLAYER)

    await bot_utils.search_player(ctx, args)


@bot.command()
async def check_list(ctx: commands.Context) -> None:
    if __debug__:
        bot_utils.logger(ctx, bot_utils.Logger.CHECK_LIST)

    await bot_utils.check_tracklist(ctx, tracklist)


@bot.command()
async def get_list(ctx: commands.Context) -> None:
    if __debug__:
        bot_utils.logger(ctx, bot_utils.Logger.GET_LIST)
    for _l in serialize_list():
        await ctx.send(_l)


@bot.command()
async def add_player(ctx: commands.Context, *args) -> None:
    if __debug__:
        bot_utils.logger(ctx, bot_utils.Logger.ADD_PLAYER)

    if username := " ".join(args):
        if username in ("Player",):
            await ctx.send("srysly??")
        else:
            if (logs := loglist.get(username)) and any(
                log.log_type is bot_utils.Logger.REMOVE_PLAYER for log in logs
            ):
                loglist.setdefault(username, []).append(
                    bot_utils.TrollTrace(
                        log_type=bot_utils.Logger.TRIED_TO_ADD,
                        sus=ctx.author.name,
                        victim=username,
                    )
                )
                await bot_utils.save_loglist(loglist)
                await ctx.send("nunu i can't do this")

            elif username in tracklist:
                await ctx.send("they are already in the tracklist")
            else:
                tracklist.add(username)
                serialize_list.cache_clear()

                loglist.setdefault(username, []).append(
                    bot_utils.TrollTrace(
                        log_type=bot_utils.Logger.ADD_PLAYER,
                        sus=ctx.author.name,
                        victim=username,
                    )
                )

                await bot_utils.save_loglist(loglist)
                await bot_utils.save_tracklist(tracklist)
                await ctx.send(f"{username} is in tracklist now")
    else:
        await bot_utils.error(ctx)


@bot.command()
async def trolltrace(ctx: commands.Context, *args) -> None:
    if (
        (username := " ".join(args))
        and (logs := loglist.get(username))
    ):
        for log in logs:
            await ctx.send(log.into_str())


@bot.command()
async def remove_player(ctx: commands.Context, *args) -> None:
    if __debug__:
        bot_utils.logger(ctx, bot_utils.Logger.REMOVE_PLAYER)

    if username := " ".join(args):
        if username in ("Player",):
            await ctx.send("srysly??")
        else:
            if username in tracklist:
                tracklist.remove(username)

                loglist.setdefault(username, []).append(
                    bot_utils.TrollTrace(
                        log_type=bot_utils.Logger.REMOVE_PLAYER,
                        sus=ctx.author.name,
                        victim=username,
                    )
                )
                serialize_list.cache_clear()

                await bot_utils.save_loglist(loglist)
                await bot_utils.save_tracklist(tracklist)
                await ctx.send(f"{username} is removed from the tracklist")
            else:
                await ctx.send("{username} not found in the tracklist")
    else:
        await bot_utils.error(ctx)


@bot.command()
async def help(ctx: commands.Context) -> None:
    if __debug__:
        bot_utils.logger(ctx, bot_utils.Logger.HELP)

    await ctx.send(embed=bot_utils.HELP_MSG)



bot.run(getenv("DISCORD_TOKEN", ""))
