from huey.contrib.djhuey import db_task
from players.models import Player
from .models import ExportLineup
from .utls import fetch_top_lines, refresh_materialized_bkg


def check_lineup(lu_dict):
    if ExportLineup.objects.filter(p1=lu_dict["p1"], p2=lu_dict["p2"], dedupe=lu_dict["dedupe"]).exists():
        return False
    return True


def add_of(lu, p):
    if "OF2" in lu:
        lu["OF3"] = p
    elif "OF1" in lu:
        lu["OF2"] = p
    else:
        lu["OF1"] = p
    return lu


def build_lineup_dict(lu, p1, p2):
    lu_dict = {}
    for i in range(1, 9):
        pos, name = lu["P" + str(i)], lu["N" + str(i)]
        if pos == "OF":
            add_of(lu_dict, name)
        else:
            lu_dict[pos] = name
    lu_dict["TMCODE"] = lu["TMCODE"]
    lu_dict["source"] = lu["Source"]
    lu_dict["pts"] = lu["PTS"]
    lu_dict["salary"] = lu["COST"]
    lu_dict["p1"] = p1.name_id
    lu_dict["p2"] = p2.name_id
    lu_dict["dedupe"] = lu["DUPE"]
    return lu_dict


def build_player_set(lu):
    return {lu.c, lu.fB, lu.sB, lu.tB, lu.ss, lu.of1, lu.of2, lu.of3}

def build_player_set_from_dict(lu):
    return {lu["C"], lu["1B"], lu["2B"], lu["3B"], lu["SS"], lu["OF1"], lu["OF2"], lu["OF3"]}

def validate_uniqueness(lu, uploaded, unique):
    unique_set = build_player_set_from_dict(lu)
    for u in uploaded:
        u_set = build_player_set(u)
        print(unique_set, u_set)
        if len(unique_set - u_set) <= unique:
            return False
    return True


def save_lus(post, user):
    punt = True if post.get('punt', "all") == "punt" else False
    p1_id = post.get("p1")
    p2_id = post.get("p2")
    unique = post.get("unique")
    p1 = Player.objects.get(id=p1_id)
    p2 = Player.objects.get(id=p2_id)
    salary = p1.salary + p2.salary
    for code, count in post.items():
        if count is None:
            count = 0
        if code not in ("p1", "p2", "csrfmiddlewaretoken", "punt") and int(count) > 0:
            print(code, count)
            lines = fetch_top_lines(50000 - salary, code, count, punt)
            fetched_line_count = len(lines)
            added = 0
            loops = 0
            while added <= count or loops <= fetched_line_count:
                print(added, count, loops, fetched_line_count)
                for lu in lines:
                    lu_dict = build_lineup_dict(lu, p1, p2)
                    uploaded = ExportLineup.objects.filter(p1=lu_dict["p1"], p2=lu_dict["p2"], combo=lu_dict["TMCODE"])
                    line_is_unique = validate_uniqueness(lu_dict, uploaded, unique)
                    if int(lu_dict["salary"]) + salary > 49000 and check_lineup(lu_dict) and line_is_unique:
                        new_line = ExportLineup(
                            user=user,
                            p1=lu_dict["p1"],
                            p2=lu_dict["p2"],
                            c=lu_dict["C"],
                            fB=lu_dict["1B"],
                            sB=lu_dict["2B"],
                            tB=lu_dict["3B"],
                            ss=lu_dict["SS"],
                            of1=lu_dict["OF1"],
                            of2=lu_dict["OF2"],
                            of3=lu_dict["OF3"],
                            salary=int(lu_dict["salary"]) + salary,
                            team1=lu["TM"],
                            team2=lu["TM2"],
                            combo=lu_dict["TMCODE"],
                            lu_type=lu_dict["source"],
                            dedupe=lu_dict["dedupe"],
                        )
                        new_line.save()
                        added += 1
                        print("saved")
                    else:
                        print("Salary To Low")
                    loops += 1


@db_task()
def refresh_bkg():
    refresh_materialized_bkg()
