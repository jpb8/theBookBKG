from django.db import connection
from players.models import Player
from .models import ExportLineup

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def all_lines(cost):
    with connection.cursor() as cursor:
        cursor.execute('''select count(l."TMCODE") as lus, l."TMCODE" 
                        from bkg_slate_lus l  where l."COST"<={} group by l."TMCODE";
                        '''.format(cost))
        qs = dictfetchall(cursor)
    return qs


def fetch_top_lines(cost, team_code, count):
    with connection.cursor() as cursor:
        cursor.execute('''
                        select * from bkg_slate_lus l 
                        where l."TMCODE" = '{}' and l."COST"<={} 
                        order by l."COST" desc, l."PTS" desc limit {};
                        '''.format(team_code, cost, count))
        qs = dictfetchall(cursor)
    return qs


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
    for i in range(1, 8):
        pos, name = getattr(lu, "P" + str(i)), getattr(lu, "N" + str(i))
        if pos == "OF":
            add_of(lu_dict, name)
        else:
            lu_dict[pos] = name
    lu_dict["TMCODE"] = lu.TMCODE
    lu_dict["source"] = lu.Source
    lu_dict["pts"] = lu.PTS
    lu_dict["p1"] = p1.name_id
    lu_dict["p2"] = p2.name_id
    return lu_dict


def save_lu(lu, p1, p2):
    lu_dict = {}
    return lu_dict
