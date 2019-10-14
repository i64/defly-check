import json

TEAM_MAP = {2: "Blue", 3: "Red", 4: "Dark Green", 5: "Orange", 6: "Purple", 7: "Sky Blue", 8: "Green", 9: "Pink"}
TEAM_NAMES = ["Blue", "Red", "Dark Green", "Orange", "Purple", "Sky Blue", "Green", "Pink"]


def get_table(tbl, borderHorizontal="-", borderVertical="|", borderCross="+"):
    cols = [list(x) for x in zip(*tbl)]
    lengths = [max(map(len, map(str, col))) for col in cols]

    f = borderVertical + borderVertical.join(" {:>%d} " % l for l in lengths) + borderVertical
    s = borderCross + borderCross.join(borderHorizontal * (l + 2) for l in lengths) + borderCross

    result = s + "\n"
    for row in tbl:
        result += f.format(*row) + "\n"
        result += s + "\n"
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
    parsen.append(["Team Name", "Map Control", "Space", "Players"])
    for team in teams:
        parsen.append(parse_team(team))
    return get_table(parsen)
