import aiofiles as aiof

from discord import Embed, Colour
from discord.ext.commands import Context

from parser import Player, Team, Server
import defly_check

import json

from enum import IntEnum
import dataclasses

from typing import Any, Dict, List, Optional, Set, Tuple


class Logger(IntEnum):
    CHECK_SERVER = 0
    CHECK_SERVERS = 1
    SEARCH_PLAYER = 2
    CHECK_LIST = 3
    GET_LIST = 4
    ADD_PLAYER = 5
    TRIED_TO_ADD = 6
    REMOVE_PLAYER = 7
    HELP = 8
    GET_LINK = 9

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

@dataclasses.dataclass
class TrollTrace():
    log_type: Logger
    sus: str
    victim: str

    def into_str(self):
        return f"**LOG**: `{self.sus}` -> `{self.log_type.name}` -> `{self.victim}`"

    @classmethod
    def from_dict(cls, elems):
        return cls(
            log_type=Logger(elems["log_type"]),
            sus=elems["sus"],
            victim=elems["victim"],
        )

TRACK_LIST = "good_players.json"
LOG_LIST = "track_logs.json"

REGIONS = dict(
    EU1="eu1-1",
    USE1="use4",
    USW1="usw4",
    # "TOK1",
    # "SA1",
    # "RU1",
    # "AU",
)

REGION_NAMES = frozenset(REGIONS.keys())

REGIONS_STRING = ", ".join(REGIONS.keys())

TEAM_MAP = {
    2: ("Blue", 0x3D5DFF),
    3: ("Red", 0xFD3535),
    4: ("D-Green", 0x008037),
    5: ("Orange", 0xFF8A2A),
    6: ("Purple", 0x924BFF),
    7: ("S-Blue", 0x55D5FF),
    8: ("Green", 0x18E21F),
    9: ("Pink", 0xF659FF),
}
TEAMS_TITLE = ["Team", "Map %", "Ppl", "Players"]


HELP_MSG = Embed()

HELP_MSG.add_field(
    name="!check_server REGION [PORT]", value="checks server", inline=False
)
HELP_MSG.add_field(
    name="!check_servers [PORT]", value="checks all active servers", inline=False
)

HELP_MSG.add_field(name="!check_list ", value="check the player list", inline=False)
HELP_MSG.add_field(
    name="!add_player PLAYER_NAME", value="adds the player into the list", inline=False,
)
HELP_MSG.add_field(
    name="!remove_player PLAYER_NAME",
    value="removes the player from the list",
    inline=False,
)
HELP_MSG.add_field(name="!get_list", value="returns the list", inline=False)
HELP_MSG.add_field(
    name="!get_link REGION PORT",
    value="returns a link for the given link",
    inline=False,
)

HELP_MSG.add_field(
    name="!search_player PLAYER_NAME",
    value="checks if the player is online",
    inline=False,
)

HELP_MSG.add_field(name="!help", value="Gives this message", inline=False)


async def error(ctx: Context) -> None:
    ctx.send("wrong command usage please check `!help` command")


def serialize_user(players: List[Player]) -> str:
    return "".join(player.username for player in players)


def serialize_team(team: Team) -> List[str]:
    result = list()
    result.append(TEAM_MAP[team.team_id][0])
    result.append(format(team.map_percent, ".2f"))
    result.append(f"{6}/{len(team.players)}")
    result.append(
        "'"
        + "', '".join(
            player.username.replace("'", "").replace('"', "").replace("````", "")
            for player in team.players.values()
        )
        + "'"
    )  # bu ne aq cok usendim duzeltmeye

    return result


def serialize_server(server: Server) -> str:
    seriealized_teams = [serialize_team(team) for team in server.teams]
    return get_table(TEAMS_TITLE, seriealized_teams)


def get_table(titles: Any, rows: List[List[str]]) -> str:
    widths = [max(map(len, map(str, col))) for col in zip(*rows)]
    header = "  ".join((str(val).ljust(width) for val, width in zip(titles, widths)))
    body = "\n".join(
        [
            ("  ".join((str(val).ljust(width) for val, width in zip(row, widths))))
            for row in rows
        ]
    )
    return f"{header}\n\n{body}"


async def check_tracklist(ctx: Context, tracklist: Set[str]) -> None:
    done = False
    async for players, header, server in defly_check._gen_check_tracklist(tracklist):
        done = True
        _len = len(players) > 1
        await ctx.send(
            f"ya ya, {', '.join(f'`{player}`' for player in players)} {'are' if _len else 'is'} online lets go 🥺👉👈 {'them' if _len else 'him/her'}"
        )
        await send_server(ctx, header, server)
    else:
        if not done:
            await ctx.send("all of them are offline -.-")


def logger(ctx: Context, _type: Logger) -> None:
    print(ctx.author.name, _type.name)


def load_tracklist() -> Set[str]:
    with open(TRACK_LIST) as fp:
        return set(json.load(fp))

def load_loglist() -> Dict[str, List[TrollTrace]]:
    with open(LOG_LIST) as fp:
        return {
            key: [TrollTrace.from_dict(elem) for elem in value]
            for key, value in json.load(fp).items()
        }


async def save_loglist(logs:  Dict[str, List[TrollTrace]]):
    async with aiof.open(LOG_LIST, "w") as out:
        await out.write(json.dumps(logs, cls=EnhancedJSONEncoder))
        
async def save_tracklist(tracklist: Set[str]):
    async with aiof.open(TRACK_LIST, "w") as out:
        await out.write(json.dumps(list(tracklist)))


def quote(data: str, f_format: Optional[str] = None) -> str:
    if f_format:
        return f"```{f_format}\n```"
    return f"```{data}```"


def get_link(
    region: str, port: str, game_mode: defly_check.GameModes = defly_check.GameModes.TEAMS
):
    if region_id := REGIONS.get(region.upper()):
        return f"https://defly.io/#{game_mode.value}-{region_id}.:{port}"
    return f"region the region name please. ({region} not found).\n all regions are: {REGIONS_STRING}"


def region_with_port(uri: str) -> str:
    region, port = uri.split(".defly.io:")
    return f"{region} {port}"


def get_url(header: str):
    return f"https://defly.io/#1-{header.replace('defly.io', '')}"


async def send_server(ctx: Context, header: str, server: Server) -> None:
    embed = Embed(
        title=f"**{region_with_port(header)}**",
        colour=Colour(
            TEAM_MAP[max(server.teams, key=lambda team: team.map_percent).team_id][1]
        ),
        url=get_url(header),
        description=quote(serialize_server(server)),
    )
    await ctx.send(embed=embed)


async def _check_servers(ctx: Context, port: Optional[str] = None) -> None:
    async for uri, server in defly_check.check_servers(port=port):
        if server:
            await send_server(ctx, uri, server)


async def search_player(ctx: Context, args: Tuple[Any, ...]) -> None:
    username = " ".join(args)
    if username:
        if username != "Player":
            if _data := await defly_check.search_player(username, bot=True):
                header, server = _data
                await ctx.send(f"ya ya, {username} is online lets go 🥺🥺🥺👉👈 him/her")
                await send_server(ctx, header, server)
            else:
                await ctx.send("no he/she is not online :(")
        else:
            await ctx.send("srysly??")
    else:
        await error(ctx)


async def check_server(ctx: Context, region: str, port: Optional[int] = None) -> None:
    if (region := region.upper()) in REGION_NAMES:
        if port:
            _, data = await defly_check.check_server(region, port=port, bot=True)  # type: ignore
            await send_server(ctx, f"{region} {port}", data)
        else:
            for _port in defly_check.KNOWN_PORTS:
                uri, data = await defly_check.check_server(region, port=_port, bot=True)  # type: ignore
                if data:
                    await send_server(ctx, uri, data)
                else:
                    await ctx.send(f"{uri} is above of %80")
    else:
        await ctx.send(f"hey, hey. check the region please {REGIONS_STRING}")


async def check_servers(ctx: Context, port: Optional[str] = None):
    if port:
        await _check_servers(ctx, port)
    else:
        for _port in defly_check.KNOWN_PORTS:
            await _check_servers(ctx, _port)

