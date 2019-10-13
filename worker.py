from parser import Parser
import requests
import websockets
import asyncio


class Worker():
    GEN_ENDPOINT = "https://s.defly.io/?r={}&m={}"
    REGION_LIST = ['EU1', 'TOK1', 'SA1', 'RU1', 'USE1', 'USW1', 'AU']
    @staticmethod
    async def _check_server(server, auth):
        async with websockets.connect(f"wss://{server.replace(':', '/')}") as websocket:
            await websocket.send(bytearray(auth))
            users = list()
            while True:
                try:
                    data = await websocket.recv()
                    res = Parser.parser(data, users, websocket)
                    if res:
                        if res[0].get('available') != None:
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
                
    @staticmethod
    def get_server(area: str, m: int):
        resp = requests.get(Worker.GEN_ENDPOINT.format(area, m)).text
        return resp.split(" ")

    @staticmethod
    def check_server(area: str, m=1):
        server, token = Worker.get_server(area, m)
        auth = ("Player", token)
        loop = asyncio.new_event_loop()
        phase = Parser.create_login_phase(*auth, skin=1, game_played=0)
        return loop.run_until_complete(Worker._check_server(server, phase))
    
    @staticmethod
    def check_servers(m=1):
        result = dict()
        for region in Worker.REGION_LIST:
            ## =: walrus walrus walrus walrus :=
            _server = Worker.check_server(region, m=m)
            result[region] = _server
        return result

    @staticmethod
    def check_available(server: str, area: str, m: int, username: str, token: str):
        params = {
            'r': area,
            'm': m,
            's': token,
            'p': server.replace("defly.io", ''),
            'u': username,
        }
        response = requests.post('http://s.defly.io/', params=params, verify=False, timeout=2)
        
        return not response.text.startswith("ER")

