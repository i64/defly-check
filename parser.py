from dataview import DataView
import websockets

from typing import Dict, List, Optional, Union
from dataclasses import dataclass

import itertools


@dataclass
class Player:
    player_id: int
    username: str
    skin_id: int
    badge_id: Optional[int] = 0


@dataclass
class Team:
    team_id: int
    map_percent: float
    available: bool
    players: Dict[int, Player]


@dataclass
class Server:
    teams: List[Team]
    team_size: int
    team_count: int


def get_str(data: DataView, offset: int) -> str:
    size = data.get_uint_8(offset)
    offset += 1
    return "".join(
        [
            chr(
                data.get_uint_8((idx := (offset + 2 * counter)) + 1)
                | data.get_uint_8(idx) << 8
            )
            for counter in range(size)
        ]
    )


def parse_user(_data: bytes) -> Union[Player, int]:
    data = DataView(_data)
    player_id = data.get_int_32(size := 1)
    username = get_str(data, size := size + 4)
    skin_id = data.get_int_32(size := size + 2 * len(username) + 1)
    badge = 0

    if len(data) >= (size := size + 4 + 4) - 1:
        if data.get_int_32(size - 4) == -1:  # left?
            return player_id
    if len(data) >= size + 1:
        badge = data.get_uint_8(size)

    return Player(
        player_id=player_id, username=username, skin_id=skin_id, badge_id=badge
    )


def parse_teams(_data: bytes, _players: Dict[int, Player]) -> Server:
    data = DataView(_data)

    team_size = data.get_uint_8(1)
    team_count = data.get_uint_8(2)

    server = Server(teams=list(), team_size=team_size, team_count=team_count)

    offset = 3
    for _ in itertools.repeat(None, team_count):
        team_id = data.get_uint_32(offset)

        map_percent = data.get_float_32(offset := offset + 4)
        map_percent = max(0, map_percent)

        available = bool(data.get_uint_8(offset := offset + 4))

        member_limit = data.get_uint_8(offset := offset + 1)
        offset += 1
        players: Dict[int, Player] = dict()
        for _ in itertools.repeat(None, member_limit):
            player_id = data.get_int_32(offset)
            players[player_id] = _players[player_id]
            offset += 4

        server.teams.append(
            Team(
                team_id=team_id,
                map_percent=map_percent,
                available=available,
                players=players,
            )
        )

    return server


async def parser(
    data: bytes,
    players: Dict[int, Player],
    websocket: websockets.WebSocketClientProtocol,
) -> Optional[Server]:
    header_byte = data[0]
    if header_byte == 29:
        if isinstance(_user := parse_user(data), int):  # if the user not there anymore
            players = {_user: players[_user]}
        else:
            players[_user.player_id] = _user
    elif header_byte == 35:
        await websocket.close()
        return parse_teams(data, players)
    return None


def create_login_phase(username: str, token: str, skin: int, game_played: int) -> bytes:
    buffer = DataView(
        b"\x00" * (2 + (2 * len(username)) + 1 + (2 * len(token)) + 4 + 4)
    )
    buffer.set_uint_8(idx := 0, 1)
    buffer.write_string(idx := idx + 1, username)
    buffer.write_string(idx := idx + 1 + 2 * len(username), token)
    buffer.set_int_32(idx := idx + 1 + 2 * len(token), skin)
    buffer.set_int_32(idx := idx + 4, game_played)
    return buffer.array
