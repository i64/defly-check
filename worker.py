import parser
import requests
import websockets
import asyncio


GEN_ENDPOINT = "https://s.defly.io/?r={}&m={}"
REGION_LIST = ["EU1", "TOK1", "SA1", "RU1", "USE1", "USW1", "AU"]


async def _check_server(server, auth):
    async with websockets.connect(f"wss://{server.replace(':', '/')}") as websocket:
        await websocket.send(bytes(auth))
        users = list()
        while True:
            try:
                data = await websocket.recv()
                print(data)
                res = parser.parser(data, users, websocket)
                if res:
                    if res[0].get("available") != None:
                        for team in res:
                            members = list()
                            for member_id in team.get("members"):
                                member = list(filter(lambda user: user.get("user_id") == member_id, users))
                                if member:
                                    members.append(member)
                            team["members"] = members
                        return res
            except (websockets.exceptions.ConnectionClosed):
                break


def get_server(area: str, m: int):
    resp = requests.get(GEN_ENDPOINT.format(area, m)).text
    return resp.split(" ")


def check_server(area: str, m=1):
    server, token = get_server(area, m)
    auth = ("Player", token)
    loop = asyncio.new_event_loop()
    phase = parser.create_login_phase(*auth, skin=1, game_played=0)
    return loop.run_until_complete(_check_server(server, phase))


def check_server_by_port(area: str, port=3005, m=1):
    server, token = get_server(area, m)
    server = f"{server.split(':')[0]}:{str(port)}"
    # print(server)
    auth = ("Player", token)
    loop = asyncio.new_event_loop()
    phase = parser.create_login_phase(*auth, skin=1, game_played=0)
    return loop.run_until_complete(_check_server(server, phase))


def check_servers(m=1):
    result = dict()
    for region in REGION_LIST:
        # =: walrus walrus walrus walrus :=
        _server = check_server(region, m=m)
        result[region] = _server
    return result


def check_available(server: str, area: str, m: int, username: str, token: str):
    params = {"r": area, "m": m, "s": token, "p": server.replace("defly.io", ""), "u": username}
    response = requests.post("http://s.defly.io/", params=params, verify=False, timeout=2)

    return not response.text.startswith("ER")
