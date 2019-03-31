from huey.contrib.djhuey import db_task
from players.models import Player
from .models import ExportLineup
from .utls import fetch_top_lines

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


@db_task()
def save_lus(request):
    user = request.user
    p1_id = request.POST.get("p1")
    p2_id = request.POST.get("p2")
    p1 = Player.objects.get(id=p1_id)
    p2 = Player.objects.get(id=p2_id)
    salary = p1.salary + p2.salary
    for k, v in request.POST.items():
        if k not in ("p1", "p2", "csrfmiddlewaretoken"):
            lines = fetch_top_lines(50000 - salary, k, v)
        for lu in lines:
            lu_dict = build_lineup_dict(lu, p1, p2)
            ExportLineup(
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
                team1=lu.TM1,
                team2=lu.TM2,
                combo=lu_dict["TMCODE"],
                lu_type=lu_dict["source"],
            )
            ExportLineup.save()

