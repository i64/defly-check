from dataview import DataView
import websockets


def get_str(data: DataView, offset: int):
    size = data.get_uint_8(offset)
    offset += 1

    result = str()
    for counter in range(size):
        result += chr(data.get_uint_8(offset + 2 * counter + 1) | data.get_uint_8(offset + 2 * counter + 0) << 8)

    return result


def parse_user(_data):
    data = DataView(_data)
    user_id = data.get_int_32(1)
    username = get_str(data, 5)
    skin_id = data.get_int_32(6 + 2 * len(username))

    len_checker = 6 + 2 * len(username) + 4 + 4 - 1
    if data.length >= len_checker:
        if data.get_int_32(len_checker) == -1:
            return user_id
    return dict(user_id=user_id, username=username, skin_id=skin_id)


def parse_teams(_data: bytes):
    data = DataView(_data)
    max_user_per_team = data.get_uint_8(1)
    team_count = data.get_uint_8(2)

    teams = list()

    iter_counter = 3
    for _ in range(team_count):
        team_id = data.get_uint_32(iter_counter)
        map_percent = data.get_float_32(iter_counter + 4)
        available = bool(data.get_uint_8(iter_counter + 8))

        member_limit = data.get_uint_8(iter_counter + 9)
        iter_counter += 10
        members = list()
        for member_id in range(member_limit):
            members.append(data.get_int_32(iter_counter))
            iter_counter += 4
        teams.append(dict(team_id=team_id, map_percent=map_percent, available=available, members=members))

    return teams


def parser(data: bytes, users: list, websocket: websockets.WebSocketClientProtocol):
    header_byte = data[0]
    if header_byte == 29:
        ret = parse_user(data)
        if type(ret) == int:
            users = list(filter(lambda user: user["user_id"] != ret, users))
        else:
            users.append(ret)
        return users
    elif header_byte == 35:
        websocket.close()
        return parse_teams(data)


def create_login_phase(username: str, token: str, skin: int, game_played: int) -> bytes:
    buffer = DataView(b"\x00" * (2 + (len(username) * 2) + 1 + (2 * len(token)) + 4 + 4))
    idx = 0
    buffer.set_uint_8(idx, 1)
    idx += 1
    buffer.write_string(idx, username)
    idx += 1 + 2 * len(username)
    buffer.write_string(idx, token)
    idx += 1 + 2 * len(token)
    buffer.set_int_32(idx, skin)
    idx += 4
    buffer.set_int_32(idx, game_played)

    return buffer.array
