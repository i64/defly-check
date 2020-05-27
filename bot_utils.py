import json
import worker

from typing import Optional

from discord.ext.commands import Context

from typing import Any, List, Optional, Set


from parser import Player, Team, Server

from enum import Enum


class Logger(Enum):
    CHECK_SERVER = 0
    CHECK_SERVERS = 1
    SEARCH_PLAYER = 2
    CHECK_LIST = 3
    GET_LIST = 4
    ADD_PLAYER = 5
    HELP = 6


TRACK_LIST = "good_players.json"

REGIONS = frozenset(
    {
        "EU1",
        # "TOK1",
        # "SA1",
        # "RU1",
        "USE1",
        "USW1",
        # "AU",
    }
)

REGIONS_STRING = ", ".join(REGIONS)

TEAM_MAP = {
    2: "Blue",
    3: "Red",
    4: "D-Green",
    5: "Orange",
    6: "Purple",
    7: "S-Blue",
    8: "Green",
    9: "Pink",
}
TEAMS_TITLE = ["Team", "Map %", "Ppl", "Players"]


async def error(ctx: Context) -> None:
    ctx.send("wrong command usage please check `!help` command")


def serialize_user(players: List[Player]) -> str:
    return "".join([player.username for player in players])


def serialize_team(team: Team) -> List[str]:
    result = list()
    result.append(TEAM_MAP[team.team_id])
    result.append(format(team.map_percent, ".2f"))
    result.append(f"{6}/{len(team.players)}")
    result.append(
        "'"
        + "','".join(
            [
                player.username.replace("'", "").replace('"', "").replace("````", "")
                for player in team.players.values()
            ]
        )
        + "'"
    )  # bu ne aq cok usendim duzeltmeye

    return result


def serialize_server(server: Server) -> str:
    seriealized_teams = [serialize_team(team) for team in server.teams]
    return get_table(TEAMS_TITLE, seriealized_teams)


def get_table(titles: Any, rows: List[List[str]]) -> str:
    titles.extend(rows)
    widths = [max(map(len, map(str, col))) for col in zip(*rows)]
    rows = [rows[0]] + [["-" * width for width in widths]] + rows[1:]
    return "\n".join(
        [
            ("  ".join((str(val).ljust(width) for val, width in zip(row, widths))))
            for row in rows
        ]
    )


async def check_tracklist(ctx: Context, tracklist: Set[str]) -> None:
    async for players, header, server in worker._gen_check_tracklist(tracklist):
        _len = len(players) > 1
        await ctx.send(
            f"ya ya, {' '.join([f'`{player}`' for player in players])} {'are' if _len else 'is'} online lets go kill {'them' if _len else 'him/her'}: https://defly.io/#1-{header.replace('defly.io', '')}"
        )
        return await send_server(ctx, header, server)
    await ctx.send("all of them are offline -.-")


def logger(ctx: Context, _type: Logger) -> None:
    print(ctx.author.name, _type.name)


def load_tracklist() -> Set[str]:
    fp = open(TRACK_LIST)
    return set(json.load(fp))


def save_tracklist(tracklist: Set[str]):
    fp = open(TRACK_LIST, "w")
    json.dump(list(tracklist), fp)
    if not fp.closed:
        fp.close()


def quote(data: str, f_format: Optional[str] = None) -> str:
    if f_format:
        return f"```{f_format}\n```"
    return f"```{data}```"


def region_with_port(uri: str) -> str:
    region, port = uri.split(".defly.io:")
    return f"{region} {port}"


async def send_server(ctx: Context, header: str, server: Server) -> None:
    _data = f"`{header}` {quote(serialize_server(server))}"
    await ctx.send(_data)


async def _check_servers(ctx: Context, port: Optional[str] = None) -> None:
    async for uri, server in worker.check_servers(port=port):
        if server:
            await send_server(ctx, region_with_port(uri), server)


async def search_player(ctx: Context, args: List[str]) -> None:
    username = " ".join(args)
    if username:
        if username != "Player":
            if _data := await worker.search_player(username, bot=True):
                header, server = _data
                await ctx.send(
                    f"ya ya, {username} is online lets go kill him: https://defly.io/#1-{header.replace('defly.io', '')}"
                )
                await send_server(ctx, header, server)
            else:
                await ctx.send("no he is not online :(")
        else:
            await ctx.send("srysly??")
    else:
        await error(ctx)


async def check_server(ctx: Context, region: str, port: Optional[int] = None) -> None:
    region = region.upper()
    if region in REGIONS:
        if port:
            _, data = await worker.check_server(region, port=port, bot=True)  # type: ignore
            await send_server(ctx, f"{region} {port}", data)
        else:
            for _port in worker.KNOWN_PORTS:
                _port, data = await worker.check_server(region, port=_port, bot=True)  # type: ignore
                _server_handler = f"{region} {_port}"
                if data:
                    await send_server(ctx, _server_handler, data)
                else:
                    await ctx.send(f"{_server_handler} are %80")
    else:
        await ctx.send(f"hey, hey. check the region please {REGIONS_STRING}")


async def check_servers(ctx: Context, port: Optional[str] = None):
    if port:
        await _check_servers(ctx, port)
    else:
        for _port in worker.KNOWN_PORTS:
            await _check_servers(ctx, _port)
