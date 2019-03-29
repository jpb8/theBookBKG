from django.db import connection

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