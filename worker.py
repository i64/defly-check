import parser
import asyncio
import aiohttp
import websockets

from contextlib import suppress

from typing import (
    List,
    Optional,
    Dict,
    Tuple,
    AsyncGenerator,
    Union,
    Set,
    TYPE_CHECKING,
)
from enum import IntEnum

from parser import Player, Server


class GameModes(IntEnum):
    FFA = 0
    TEAMS = 1
    DEFUSE = 2
    EFFA = 3


GEN_ENDPOINT = "https://s.defly.io/?r={}&m={}"
REGION_LIST = (
    "EU1",
    # "TOK1",
    # "SA1",
    # "RU1",
    "USE1",
    "USW1",
    # "AU",
)
KNOWN_PORTS = ("3005", "3015")

trd_ss = None


async def _check_server(host: str, auth: bytes) -> Optional[Server]:
    with suppress(websockets.exceptions.InvalidStatusCode):
        async with websockets.connect(f"wss://{host.replace(':', '/')}") as websocket:
            await websocket.send(auth)
            players: Dict[int, Player] = dict()
            while True:
                try:
                    data = await asyncio.wait_for(websocket.recv(), timeout=1)
                    assert isinstance(data, bytes)
                    if (
                        server := await parser.parser(data, players, websocket)
                    ) and server.teams[0].available:
                        return server
                except asyncio.TimeoutError as e:
                    return None
                except websockets.exceptions.ConnectionClosed:
                    return server


async def get_hosts(region: str, gamemode: GameModes = GameModes.TEAMS) -> List[str]:
    async with aiohttp.ClientSession() as client:
        async with client.get(GEN_ENDPOINT.format(region, gamemode)) as resp:
            text = await resp.text()
            return text.split(" ")


async def check_server(
    region: str, gamemode: GameModes = GameModes.TEAMS, port=None, bot=False
) -> Union[Server, Tuple[str, Server]]:
    uri, token, _ = await get_hosts(region, gamemode)
    if port:
        uri = f"{uri.split(':')[0]}:{str(port)}"
    server = await __get_server(uri, token)
    if bot:
        return (uri.split(":")[1], server)
    return server


async def __get_server(host: str, token: str) -> Optional[Server]:
    auth = ("Player", token)
    phase = parser.create_login_phase(*auth, skin=1, game_played=0)
    return await _check_server(host, phase)


def change_port(uri: str, port: Optional[str] = None) -> str:
    if port:
        region, _ = uri.split(":")
        return f"{region}:{port}"
    return uri


async def check_servers(
    game_mode: GameModes = GameModes.TEAMS, port: Optional[str] = None,
) -> AsyncGenerator[Tuple[str, Server], None]:
    done_list = set()
    for region in REGION_LIST:
        uri, token, _ = await get_hosts(region, game_mode)
        uri = change_port(uri, port)
        if uri not in done_list:
            done_list.add(uri)
            server = await __get_server(uri, token)
            yield (uri, server)


def get_all_usernames(server: Optional[Server]) -> List[Optional[str]]:
    result: List[Optional[str]] = list()
    if server:
        for team in server.teams:
            result.extend(player.username for player in team.players.values())
    return result


async def search_player(
    username: str, bot: bool = False
) -> Optional[Tuple[str, Server]]:
    if username in ("Player",):
        return None
    for port in KNOWN_PORTS:
        async for uri, server in check_servers(port=port):
            if username in get_all_usernames(server):
                return (uri.replace(".defly.io/", ":"), server)
    return None


async def check_available(
    server: str, region: str, m: int, username: str, token: str
) -> bool:
    params = {
        "r": region,
        "m": m,
        "s": token,
        "p": server.replace("defly.io", ""),
        "u": username,
    }
    async with aiohttp.ClientSession() as client:
        async with client.post(
            "http://s.defly.io/", params=params, verify=False, timeout=2
        ) as resp:
            text = await resp.text()
            return not text.startswith("ER")


async def _gen_check_tracklist(
    tracklist: Set[str], bot: bool = False
) -> AsyncGenerator[Tuple[Set[str], str, Server], None]:
    async for uri, server in check_servers():
        if online_players := tracklist.intersection(get_all_usernames(server)):
            yield (online_players, uri.replace(".defly.io/", ":"), server)
