import json

REGIONS_LIST = ["EU1", "TOK1", "SA1", "RU1", "USE1", "USW1", "AU"]  # evet iki defa tanimladim cunku kiroyum kiroooo
REGIONS_STRING = ", ".join(REGIONS_LIST)
TEAM_MAP = {2: "Blue", 3: "Red", 4: "D-Green", 5: "Orange", 6: "Purple", 7: "S-Blue", 8: "Green", 9: "Pink"}
# TEAM_NAMES = ["Blue", "Red", "Dark Green", "Orange", "Purple", "Sky Blue", "Green", "Pink"]


def get_table(tbl, borderHorizontal="-", borderVertical="|", borderCross="+"):
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


def check_killist(teams, killist):
    online_list = list()
    for team in teams:
        for member in teams.get("members", []):
            if member["username"] in killist:
                online_list.append((team["team_id"], member))
    return online_list


def load_killist():
    file = open("killist.json")
    return json.load(file)


def save_killist(killist):
    file = open("killist.json")
    return json.dump(file)


def parse_team(team):
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


def parse_server(teams):
    parsen = list()
    parsen.append(["Team", "Map %", "Ppl", "Players"])
    for team in teams:
        parsen.append(parse_team(team))
    return get_table(parsen)


def region_with_port(uri):
    region, port = uri.split(".defly.io:")
    return f"{region} {port}"


async def send_server(ctx, header, server):
    await ctx.send(quote(header, f_format="glsl"))
    await ctx.send(quote(parse_server(server)))
