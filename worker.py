import parser
import asyncio
import requests
import threading
import websockets

from typing import Optional

GEN_ENDPOINT = "https://s.defly.io/?r={}&m={}"
REGION_LIST = ["EU1", "TOK1", "SA1", "RU1", "USE1", "USW1", "AU"]
KNOWN_PORTS = [3005, 3015]

trd_ss = None


async def _check_server(server: str, auth: bytes):
    try:
        async with websockets.connect(f"wss://{server.replace(':', '/')}") as websocket:
            await websocket.send(auth)
            users = list()
            while True:
                try:
                    data = await websocket.recv()
                    res = parser.parser(data, users, websocket)
                    if res:
                        if res[0].get("available") != None:
                            for team in res:
                                members = list()
                                for member_id in team.get("members"):
                                    member = list(filter(lambda user: user.get("user_id") == member_id, users))
                                    if member:
                                        members.extend(member)
                                team["members"] = members
                            return res
                except (websockets.exceptions.ConnectionClosed):
                    break
    except (websockets.exceptions.InvalidStatusCode):
        pass


def get_server(region: str, m=1):
    resp = requests.get(GEN_ENDPOINT.format(region, m)).text
    return resp.split(" ")


def thread_shit(server, phase):
    global trd_ss
    loop = asyncio.new_event_loop()
    trd_ss = loop.run_until_complete(_check_server(server, phase))
    loop.stop()
    loop.close()


def check_server(region: str, m=1, port=None, bot=False):
    server, token = get_server(region, m)
    if port is not None:
        server = f"{server.split(':')[0]}:{str(port)}"
    _result = _get_server(server, token, bot=bot)
    if bot:
        return (server.split(":")[1], _result)
    return _result


def _get_server(server, token, bot=False):
    auth = ("Player", token)
    phase = parser.create_login_phase(*auth, skin=1, game_played=0)
    if bot:  # im to lazy to fix it with asyncio server
        shit = threading.Thread(target=thread_shit, args=(server, phase))
        shit.start()
        shit.join()
    else:
        thread_shit(server, phase)
    return trd_ss


def change_port(uri: str, port=None):
    if port:
        region, _port = uri.split(":")
        return f"{region}:{port}"
    return uri


def _gen_check_servers(m=1, port=None, bot=False):
    done_list = list()
    for region in REGION_LIST:
        server, token = get_server(region)
        server = change_port(server, port)
        if server not in done_list:
            done_list.append(server)
            yield (server, _get_server(server, token, bot=bot))


def check_servers(port=None, m=1, bot=False):
    result = dict()
    for uri, server in _gen_check_servers(bot=bot, port=port):
        if server:
            region, port = uri.split(":")
            result[f"{region}"] = server
    return result


def get_server_members(server):
    result = list()
    if server:
        for team in server:
            result.extend([member["username"] for member in team["members"]])
    return result


def get_team_members(team):
    return [member["username"] for member in team["members"]]


def search_player(username: str, bot=False):
    if username != "Player":
        for port in KNOWN_PORTS:
            for uri, server in _gen_check_servers(bot=bot, port=port):
                members = get_server_members(server)
                if username in members:
                    return (uri.replace(".defly.io/", ":"), server)
    return None


def check_available(server: str, region: str, m: int, username: str, token: str):
    params = {"r": region, "m": m, "s": token, "p": server.replace("defly.io", ""), "u": username}
    response = requests.post("http://s.defly.io/", params=params, verify=False, timeout=2)

    return not response.text.startswith("ER")


def _gen_check_killist(kill_list: list, bot=None):
    for uri, server in _gen_check_servers(bot=bot):
        members = get_server_members(server)
        online_members = set(kill_list).intersection(members)
        if online_members:
            yield (online_members, uri.replace(".defly.io/", ":"), server)

    # for username in kill_list:
    #     _data = .search_player(username, bot=True)  # heroku neden walrnus desteklemiyorsun mk
    #     if _data:
    #         header, server = _data
    #         await ctx.send(
    #             f"ya ya,{username} is online lets go kill him: https://defly.io/#1-{header.replace('defly.io', '')}"
    #         )
    #         await send_server(ctx, header, server)
