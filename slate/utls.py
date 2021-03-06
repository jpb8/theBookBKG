from django.db import connection
from .models import Stack
import pandas as pd


def append_stacks(lines):
    for i, l in enumerate(lines):
        l[i]["players"] = []
        for team in l["TMCODE"].split("-"):
            stack = Stack.objects.filter(team=team)
            for p in stack.players:
                l[i]["players"].append({
                    "id": p.pk,
                    "name": p.dk_name
                })
    return lines


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def all_lines(cost, punt):
    inn = "not in" if punt else "in"
    with connection.cursor() as cursor:
        cursor.execute('''select count(l."TMCODE") as lus, l."TMCODE"
                        from bkg_slate_lus l  where l."COST"<={} and l."Source" {} ('Dual', '5Man')
                        group by l."TMCODE";
                        '''.format(cost, inn))
        qs = dictfetchall(cursor)
    return qs


def fetch_top_lines(cost, team_code, count, punt):
    inn = "not in" if punt else "in"
    with connection.cursor() as cursor:
        cursor.execute('''
                        select * from bkg_slate_lus l 
                        where l."TMCODE" = '{}' and l."COST"<={} and l."Source" {} ('Dual', '5Man')
                        order by l."PTS" desc, l."COST" desc;
                        '''.format(team_code, cost, inn))
        qs = dictfetchall(cursor)
    return qs


def fetch_team_lines(cost, team_code, blacklist, opp1="BLANK", opp2="BLANK"):
    bl_sql = ""
    if len(blacklist) > 0:
        bl_sql = " and ("
        for b in blacklist:
            bl_sql += '''l."DUPE" not like '%{}%' and '''.format(b)
        bl_sql = "{})".format(bl_sql.rstrip(" and "))
    with connection.cursor() as cursor:
        cursor.execute('''
                        select * from bkg_slate_lus l 
                        where l."TMCODE" LIKE '%{}%' 
                        and (l."ALLTMS" not like '%{}%' and l."ALLTMS" not like '%{}%')
                        and l."COST"<={} 
                        and l."COST">={}-1000 
                        {}
                        order by l.proj desc, l."COST" desc;
                        '''.format(team_code, opp1, opp2, cost, cost, bl_sql))
        qs = dictfetchall(cursor)
        if len(qs) == 0:
            print("{} is empty with blacklist {} and cost {}".format(team_code, blacklist, cost))
    return qs


def pitcher_cnt(user):
    with connection.cursor() as cursor:
        cursor.execute('''
                        with pitch as (select p1 as p from slate_exportlineup where user_id={} 
                        union all select p2 as p from slate_exportlineup where user_id={})
                        select count(p) as cnt, p from pitch group by p;
                        '''.format(user, user))
        qs = dictfetchall(cursor)
    return qs


def tm_cnt(user):
    with connection.cursor() as cursor:
        cursor.execute('''
                        with tms as (select team1 as tm from slate_exportlineup where user_id={}
                        union all select team2 as tm from slate_exportlineup 
                        where user_id={} and lu_type<>'5Man' and lu_type<>'4Man')
                        select count(tm) as cnt, tm from tms group by tm;
                        '''.format(user, user))
        qs = dictfetchall(cursor)
    return qs


def hitter_cnt(user):
    with connection.cursor() as cursor:
        cursor.execute('''
                        with t as (select * from slate_exportlineup where user_id={user}),
                        tot as (select count(*) as cnt from slate_exportlineup where user_id={user}), 
                        a as (select "fB" as p from t union all select "sB" as p from t 
                        union all select "tB" as p from t union all select ss from t
                        union all select of1 from t as p union all select of2 as p from t 
                        union all select of3 as p from t union all select c as p from t), 
                        p as (select count(p) as cnt, p, tot.cnt as totcnt from a, tot group by p, tot.cnt), 
                        starters as (select pp.dk_name, tt.opp
                        from players_player pp
                        left join teams_team tt on tt.dk_name = pp.team
                        where pp.starting = true)
                        select p.p, p.cnt, pp.pown, pp."position" as pos, pp.second_pos as pos2, 
                        starters.dk_name as opp, pp.team, pp.salary as sal,
                        round(((p.cnt::numeric/p.totcnt::numeric) - pp.pown),2) as field,
                        round((p.cnt::numeric/p.totcnt::numeric),2) as myPown
                        from p
                        left join players_player pp on pp.name_id = p.p
                        left join starters on starters.opp = pp.team
                        order by p.cnt desc;
                        '''.format(user=user))
        qs = dictfetchall(cursor)
    return qs


def not_in_order_players(user):
    with connection.cursor() as cursor:
        cursor.execute('''
                        with t as (select * from slate_exportlineup where user_id={}),
                        a as (select "fB" as p from t union all select "sB" as p from t 
                        union all select "tB" as p from t union all select ss from t
                        union all select of1 from t as p union all select of2 as p from t 
                        union all select of3 as p from t union all select c as p from t)
                        select p, count(p) as cnt from a group by p 
                        having p not in (select name_id from players_player where order_pos > 0)
                        order by count(p) desc;
                        '''.format(user))
        qs = dictfetchall(cursor)
    return qs


def refresh_materialized_bkg():
    with connection.cursor() as cursor:
        cursor.execute('''REFRESH MATERIALIZED VIEW bkg_slate_lus;''')


def update_team_pown():
    with connection.cursor() as cursor:
        cursor.execute('''with team_proj as (
            select rs.team,avg(rs.proj_pown) as proj
            FROM (
                SELECT pp.team,pp.proj_pown, Rank() 
                  over (Partition BY pp.team
                        ORDER BY pp.proj_pown DESC ) AS Rank
                FROM players_player pp
                ) rs WHERE Rank <= 5
                group by rs.team
            ) 
            update teams_team tt set max_stack = tp.proj
            FROM team_proj tp
            WHERE tt.dk_name = tp.team;''')
        cursor.execute('''update players_player
            set max_pown = teams_team.max_stack
            from teams_team
            where 
            players_player.team = teams_team.dk_name and 
            players_player.order_pos > 0 and 
            players_player.max_pown < teams_team.max_stack;''')


def todays_pitchers():
    with connection.cursor() as cursor:
        cursor.execute('''
                        Select * from adv_pitch;
                        ''')
        qs = dictfetchall(cursor)
    return qs


def todays_stacks():
    with connection.cursor() as cursor:
        cursor.execute('''
                        Select * from stacks_web;
                        ''')
        qs = dictfetchall(cursor)
    return qs


def tp_utils():
    with connection.cursor() as cursor:
        cursor.execute('''
                        Select * from tp_utils;
                        ''')
        qs = dictfetchall(cursor)
    return qs


def stack_utils():
    with connection.cursor() as cursor:
        cursor.execute('''
                        Select * from stacks_utils;
                        ''')
        qs = dictfetchall(cursor)
    return qs


def pstats(team):
    with connection.cursor() as cursor:
        cursor.execute('''
                        Select * from pstats where team='{}' Order by order_pos;
                        '''.format(team))
        qs = dictfetchall(cursor)
    return qs


def team_breakdown_data(team, user):
    with connection.cursor() as cursor:
        cursor.execute('''
                        with team_lines as (
                            select * from slate_exportlineup where slate_exportlineup.combo like '%{}%' and user_id={}
                        )
                        select p1, p2, count(p1) as cnt from team_lines group by p1, p2 order by p1;
                        '''.format(team, user))
        p_combo = dictfetchall(cursor)
        cursor.execute('''
                        with t as (
                            select * from slate_exportlineup where slate_exportlineup.combo like '%{}%' and user_id={}
                        ),
                        a as (
                            select "fB" as p from t union all select "sB" as p from t 
                            union all select "tB" as p from t union all select ss from t
                            union all select of1 from t as p union all select of2 as p from t 
                            union all select of3 as p from t union all select c as p from t
                        )
                        select count(p) as cnt, p from a group by p order by cnt desc;
                        '''.format(team, user))
        batters = dictfetchall(cursor)
        cursor.execute('''
                        with t as (
                            select * from slate_exportlineup where slate_exportlineup.combo like '%{}%' and user_id={}
                        ),
                        a as (
                            select "p1" as p from t union all select "p2" as p from t 
                        )
                        select count(p) as cnt, p from a group by p order by cnt desc;
                        '''.format(team, user))
        pitchers = dictfetchall(cursor)
        cursor.execute('''
                        select count(lu_type) as cnt, lu_type as type
                        from slate_exportlineup el
                        where el.combo like '%{}%' and user_id={}
                        group by el.lu_type
                        order by count(el.lu_type) desc;
                        '''.format(team, user))
        lu_type = dictfetchall(cursor)
    return p_combo, batters, pitchers, lu_type


def indy_pitcher(pitcher):
    with connection.cursor() as cursor:
        cursor.execute('''
                        select * from pl where dk_name = '{}';
                        '''.format(pitcher))
        pl_qs = dictfetchall(cursor)
        cursor.execute('''
                        select * from pr where dk_name = '{}';
                        '''.format(pitcher))
        pr_qs = dictfetchall(cursor)
    return pr_qs, pl_qs


def pitcher_builder_combos():
    with connection.cursor() as cursor:
        cursor.execute('''
                        select pp1.name_id as "p1", pp1.id as "p1id",
                        pp2.name_id as "p2", pp2.id as "p2id",
                        round(pp1.pown*(pp2.pown/(2-pp1.pown)),2) as "percent", 
                        pp1.salary+pp2.salary as "salary"
                        from players_player pp1
                        cross join players_player pp2
                        where pp1.starting = true and pp2.starting = true and 
                        pp1.id <> pp2.id and pp1.id > pp2.id 
                        and (round(pp1.pown*(pp2.pown/(2-pp1.pown)),2)>0)
                        order by round(pp1.pown*(pp2.pown/(2-pp1.pown)),2) desc;
                        ''')
        return dictfetchall(cursor)


def projections_for_ownership():
    with connection.cursor() as cursor:
        cursor.execute(
            "select name_id, dkproj, ptsstd, team, sal, pos, tri, pown  from ownership_builder order by name_id;"
        )
        df = pd.DataFrame(cursor.fetchall())
        df.columns = [col[0] for col in cursor.description]
        return df


def total_pitcher_percent(user):
    with connection.cursor() as cursor:
        cursor.execute("""
                with un as (
                    select pc.p1_id as p, pc."percent" as tot
                    from slate_pitchercombo pc
                    where user_id = {}
                    union all
                    select pc.p2_id as p, pc."percent" as tot
                    from slate_pitchercombo pc
                    where user_id = {}
                )
                select pp.name_id as p, Sum(un.tot) as "sum"
                from un 
                left join players_player pp on pp.id = un.p
                group by pp.name_id;
            """.format(user, user))
        data = dictfetchall(cursor)
    return data


def update_players_projections():
    with connection.cursor() as cursor:
        cursor.execute("select projections_function();")

