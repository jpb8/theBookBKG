from django.db import connection


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
                        from bkg_slate_lus l  where l."COST"<={} and l."Source" {} ('5Man', 'Dual')
                        group by l."TMCODE";
                        '''.format(cost, inn))
        qs = dictfetchall(cursor)
    return qs


def fetch_top_lines(cost, team_code, count, punt):
    inn = "not in" if punt else "in"
    with connection.cursor() as cursor:
        cursor.execute('''
                        select * from bkg_slate_lus l 
                        where l."TMCODE" = '{}' and l."COST"<={} and l."Source" {} ('5Man', 'Dual')
                        order by l."COST" desc, l."PTS" desc limit {};
                        '''.format(team_code, cost, inn, count))
        qs = dictfetchall(cursor)
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
                        union all select team2 as tm from slate_exportlineup where user_id={} and lu_type='Dual')
                        select count(tm) as cnt, tm from tms group by tm;
                        '''.format(user, user))
        qs = dictfetchall(cursor)
    return qs


def hitter_cnt(user):
    with connection.cursor() as cursor:
        cursor.execute('''
                        with t as (select * from slate_exportlineup where user_id={}),
                        a as (select "fB" as p from t union all select "sB" as p from t 
                        union all select "tB" as p from t union all select ss from t
                        union all select of1 from t as p union all select of2 as p from t 
                        union all select of3 as p from t union all select c as p from t)
                        select count(p) as cnt, p from a group by p order by cnt desc;
                        '''.format(user))
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
