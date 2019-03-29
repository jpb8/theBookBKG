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
        cursor.execute('''select * from bkg_slate_lus where cost<={}'''.format(cost))
        qs = dictfetchall(cursor)
    return qs