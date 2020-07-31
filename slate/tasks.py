from huey.contrib.djhuey import db_task
from players.models import Player
from .models import ExportLineup, PitcherCombo
from .utls import fetch_top_lines, refresh_materialized_bkg, fetch_team_lines, pitcher_builder_combos
from decimal import Decimal
import math


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
    lu_dict["p1"] = p1
    lu_dict["p2"] = p2
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
        if len(unique_set - u_set) < unique:
            print("not Unique", unique_set - u_set)
            return False
    return True


def save_lus(post, user):
    punt = True if post.get('punt', "all") == "punt" else False
    p1_id = post.get("p1")
    p2_id = post.get("p2")
    unique = int(post.get("unique")) if "unique" in post else 0
    p1 = Player.objects.get(id=p1_id)
    p2 = Player.objects.get(id=p2_id)
    salary = p1.salary + p2.salary
    for code, count in post.items():
        if count is None:
            count = 0
        if code not in ("p1", "p2", "csrfmiddlewaretoken", "punt", "unique") and int(count) > 0:
            print(code, count)
            lines = fetch_top_lines(50000 - salary, code, count, punt)
            added = 0
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
                if int(added) >= int(count):
                    print("broke")
                    break


def update_pitcher_pown(pitchers):
    try:
        Player.objects.filter(starting=True).update(pown=0.0)
    except Player.DoesNotExist:
        print("No pitcher to updated POWN")
    for pid, percent in pitchers.items():
        try:
            Player.objects.filter(id=pid).update(pown=Decimal(percent))
        except Player.DoesNotExist:
            print("No pitcher to updated POWN")


def add_batter_count(lu, post, bl):
    for i in range(1, 9):
        dkid = lu["D" + str(i)]
        if dkid in post["bats"]:
            post["bats"][dkid] = post["bats"][dkid] - 1
            if post["bats"][dkid] <= 0 and dkid not in bl:
                bl.append(dkid)


def validate_lineup(lu_dict, salary):
    # Can keep a running total??? Why ping db everytime?
    # uploaded = ExportLineup.objects.filter(p1=lu_dict["p1"], p2=lu_dict["p2"], combo=lu_dict["TMCODE"])
    # if validate_uniqueness(lu_dict, uploaded, 0) and check_lineup(lu_dict) and int(lu_dict["salary"]) + salary > 49000:
    if check_lineup(lu_dict) and int(lu_dict["salary"]) + salary > 49000:
        return True, lu_dict
    else:
        return False


# def add_teams_lineups(team, count, pitchers, blacklist, user, post):
#     total_added_lineups = 0
#     for p in pitchers:
#         salary = p["salary"]
#         if p["percent"] * count < 1:
#             pcnt = math.ceil(p["percent"] * count)
#         else:
#             pcnt = round(p["percent"] * count)
#         print(team, count, pcnt, p["percent"], p["p1"], p["p2"], salary, blacklist)
#         lines = fetch_team_lines(50000 - salary, team, blacklist)
#         added = 0
#         for lu in lines:
#             lu_dict = build_lineup_dict(lu, p["p1"], p["p2"])
#             if validate_lineup(lu_dict, salary):
#                 new_line = ExportLineup(
#                     user=user,
#                     p1=lu_dict["p1"],
#                     p2=lu_dict["p2"],
#                     c=lu_dict["C"],
#                     fB=lu_dict["1B"],
#                     sB=lu_dict["2B"],
#                     tB=lu_dict["3B"],
#                     ss=lu_dict["SS"],
#                     of1=lu_dict["OF1"],
#                     of2=lu_dict["OF2"],
#                     of3=lu_dict["OF3"],
#                     salary=int(lu_dict["salary"]) + salary,
#                     team1=lu["TM"],
#                     team2=lu["TM2"],
#                     combo=lu_dict["TMCODE"],
#                     lu_type=lu_dict["source"],
#                     dedupe=lu_dict["dedupe"],
#                 )
#                 new_line.save()
#                 add_batter_count(lu, post, blacklist)
#                 added += 1
#                 total_added_lineups += 1
#                 print("saved")
#             else:
#                 print("Salary To Low")
#             if int(added) >= int(pcnt):
#                 print("broke")
#                 break
#     return total_added_lineups


def build_lineup_config(post_data, total_lineups):
    data = {"teams": {}, "bats": {}}
    for p, percent in post_data.items():
        if p.startswith("team_"):
            if float(percent) > 0:
                # count = int(total_lineups * float(percent))
                data["teams"][p.split("_")[1]] = float(percent)
        elif p.startswith("bat_"):
            if float(percent) > 0:
                batter = Player.objects.get(id=p.split("_")[1])
                count = int(total_lineups * float(percent))
                data["bats"][batter.dkid] = count
    return data


# @db_task()
# def save_lineups_new(post, user):
#     total_lineups = int(post.get("total_lus"))
#     lineup_config = build_lineup_config(post, total_lineups)
#     pitchers = PitcherCombo.objects.import_data(user)
#     blacklist = []
#     total_added = 0
#     for code, count in lineup_config["teams"].items():
#         added = 0
#         if int(count) > 0:
#             added = add_teams_lineups(code, count, pitchers, blacklist, user, lineup_config)
#         if int(count) - added > 0:
#             added += add_teams_lineups(code, int(count) - added, pitchers, blacklist, user, lineup_config)
#         if int(count) - added > 0:
#             added += add_teams_lineups(code, int(count) - added, pitchers, [], user, lineup_config)
#         print("Added {} lineups for {}".format(added, code))
#         total_added += added
#         if total_added >= total_lineups:
#             break
#     print("Missed {} lineups".format(total_lineups - total_added))


def add_pitchers_lineups(p_combo, lu_config, blacklist, user, pc_cnt, remaining):
    total_added_lineups = 0
    for code, percent in lu_config["teams"].items():
        if percent * pc_cnt < 1:
            tcnt = math.ceil(percent * pc_cnt)
        else:
            tcnt = round(percent * pc_cnt)
        lines = fetch_team_lines(50000 - p_combo["salary"], code, blacklist, p_combo["opp1"], p_combo["opp2"])
        added = 0
        for lu in lines:
            lu_dict = build_lineup_dict(lu, p_combo["p1"], p_combo["p2"])
            if validate_lineup(lu_dict, p_combo["salary"]):
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
                    salary=int(lu_dict["salary"]) + p_combo["salary"],
                    team1=lu["TM"],
                    team2=lu["TM2"],
                    combo=lu_dict["TMCODE"],
                    lu_type=lu_dict["source"],
                    dedupe=lu_dict["dedupe"],
                )
                new_line.save()
                add_batter_count(lu, lu_config, blacklist)
                added += 1
                total_added_lineups += 1
                print("saved")
            else:
                print("Salary To Low")
            if int(added) >= int(tcnt) or added >= pc_cnt or total_added_lineups >= remaining:
                print("broke")
                break
        if total_added_lineups >= remaining:
            break
    return total_added_lineups


@db_task()
def save_lineups_new_pitchers_first(post, user):
    total_lineups = int(post.get("total_lus"))
    lineup_config = build_lineup_config(post, total_lineups)
    pitchers = PitcherCombo.objects.import_data(user)
    blacklist = []
    total_added = 0
    for pc in pitchers:
        pc_cnt = round(pc["percent"] * total_lineups)
        added = add_pitchers_lineups(pc, lineup_config, blacklist, user, pc_cnt, total_lineups - total_added)
        if added < pc_cnt:
            added += add_pitchers_lineups(pc, lineup_config, blacklist, user, pc_cnt - added,
                                          total_lineups - total_added)
        total_added += added
    print("Missed {} lineups".format(total_lineups - total_added))


@db_task()
def refresh_bkg():
    refresh_materialized_bkg()
