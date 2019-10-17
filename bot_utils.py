import json
import worker

from typing import Optional

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

## bot utils is not a class cuz ctx is connection object

ANGEL_NAMES = json.load(open("angels.json"))
REGIONS_LIST = ["EU1", "TOK1", "SA1", "RU1", "USE1", "USW1", "AU"]  # evet iki defa tanimladim cunku kiroyum kiroooo
REGIONS_STRING = ", ".join(REGIONS_LIST)

TEAM_MAP = {2: "Blue", 3: "Red", 4: "D-Green", 5: "Orange", 6: "Purple", 7: "S-Blue", 8: "Green", 9: "Pink"}

# TEAM_NAMES = ["Blue", "Red", "Dark Green", "Orange", "Purple", "Sky Blue", "Green", "Pink"]


async def error(ctx):
    ctx.send("wrong command usage please check `!help` command")


def get_table(tbl: list, borderHorizontal="-", borderVertical="|", borderCross="+"):
    cols = [list(x) for x in zip(*tbl)]
    lengths = [max(map(len, map(str, col))) for col in cols]

    f = borderVertical + borderVertical.join(" {:>%d} " % l for l in lengths) + borderVertical
    s = borderCross + borderCross.join(borderHorizontal * (l + 2) for l in lengths) + borderCross

    header = True
    result = str()
    for row in tbl:
        result += f.format(*row) + "\n"
        if header:
            result += s + "\n"
            header = False
    return result


async def check_killist(ctx, kill_list: list):
    for members, header, server in worker._gen_check_killist(kill_list, bot=True):
        await ctx.send(
            f"ya ya, {' '.join(list(map(lambda x: f'`{x}`', members)))} {'are' if len(members) > 1 else 'is'} online lets go kill him: https://defly.io/#1-{header.replace('defly.io', '')}"
        )
        await send_server(ctx, header, server)


def load_killist():
    file = open("killist.json")
    return json.load(file)


def save_killist(killist):
    file = open("killist.json", "w")
    json.dump(killist, file)
    if not file.closed:
        file.close()


def parse_team(team: dict):
    result = list()
    result.append(TEAM_MAP[team["team_id"]])
    result.append(format(team["map_percent"], ".2f"))
    result.append(f"6/{len(team['members'])}")
    result.append(
        "'" + "','".join([member["username"].replace("'", "").replace('"', "") for member in team["members"]]) + "'"
    )  # bu ne aq cok usendim duzeltmeye

    return result


def quote(data: str, f_format=None):
    if f_format:
        return f"```{f_format}\n#{data}\n```"
    return f"```{data}```"


def parse_server(teams: list):
    parsen = list()
    parsen.append(["Team", "Map %", "Ppl", "Players"])
    for team in teams:
        parsen.append(parse_team(team))
    return get_table(parsen)


def region_with_port(uri: str):
    region, port = uri.split(".defly.io:")
    return f"{region} {port}"


async def send_server(ctx, header: str, server: str):
    _data = f"`{header}` {quote(parse_server(server))}"
    await ctx.send(_data)


async def _check_servers(ctx, port=None):
    for uri, server in worker._gen_check_servers(bot=True, port=port):
        if server:
            await send_server(ctx, region_with_port(uri), server)


async def seek_angels(ctx, args):
    username = "".join(args)
    username = username.upper()
    result = str()
    f = True
    if username.upper() == "AZAZEL" or username.upper() == "LUCIFER":
        return await ctx.send("he is not an angel anymore :(")

    for angel in ANGEL_NAMES:
        if fuzz.partial_ratio(username, angel) >= 80:
            result += f"maybe he is an angel, its similar to {angel}\n"
            f = False

    if f and username.endswith("el") or username.endswith("al"):
        result = "yup it's an angel from -el/al family"
    
    return await ctx.send(result)


async def search_player(ctx, args):
    username = " ".join(args)
    if username:
        if username != "Player":
            _data = worker.search_player(username, bot=True)  # heroku neden walrnus desteklemiyorsun mk
            if _data:
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


async def check_server(ctx, region: str, port: Optional[int] = None):
    region = region.upper()
    if region in REGIONS_LIST:
        if not port:
            for port in worker.KNOWN_PORTS:
                port, data = worker.check_server(region, port=port, bot=True)
                await send_server(ctx, f"{region} {port}", data)
        else:
            port, data = worker.check_server(region, port=port, bot=True)
            await send_server(ctx, f"{region} {port}", data)
    else:
        await ctx.send(f"hey, hey. check the region please {REGIONS_STRING}")


async def check_servers(ctx, port: Optional[int] = None):
    if not port:
        for port in worker.KNOWN_PORTS:
            await _check_servers(ctx, port)
    else:
        await _check_servers(ctx, port)
