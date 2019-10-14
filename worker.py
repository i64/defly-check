import parser
import asyncio
import requests
import threading
import websockets


GEN_ENDPOINT = "https://s.defly.io/?r={}&m={}"
REGION_LIST = ["EU1", "TOK1", "SA1", "RU1", "USE1", "USW1", "AU"]

trd_ss = None


async def _check_server(server, auth):
    async with websockets.connect(f"wss://{server.replace(':', '/')}") as websocket:
        await websocket.send(bytes(auth))
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


def get_server(region: str, m: int):
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
    return _check_server(server, token, bot=bot)


def _check_server(server, token, bot=False):
    auth = ("Player", token)
    phase = parser.create_login_phase(*auth, skin=1, game_played=0)
    if bot:  # im to lazy to fix it with asyncio server
        shit = threading.Thread(target=thread_shit, args=(server, phase))
        shit.start()
        shit.join()
    else:
        thread_shit(server, phase)
    return trd_ss


def check_servers(m=1, bot=False):
    result = dict()
    done_list = list()
    for region in REGION_LIST:
        server, token = get_server(region, m)
        if server not in done_list:
            result[region] = _check_server(server, token)
        done_list.append(server)
    return result


def check_available(server: str, region: str, m: int, username: str, token: str):
    params = {"r": region, "m": m, "s": token, "p": server.replace("defly.io", ""), "u": username}
    response = requests.post("http://s.defly.io/", params=params, verify=False, timeout=2)

    return not response.text.startswith("ER")
