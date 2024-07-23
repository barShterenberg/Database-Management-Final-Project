from django.shortcuts import render
from .models import *
from django.db import connection


def dictfetchall(cursor):
    # Returns all rows from a cursor as a dict '''
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def index(request):
    return render(request, 'index.html')


def Query_Results(request):
    sql1 = """select md.genre, mdg.title, md.duration
from Max_duration_by_genre mdg, Max_duration md
where md.genre=mdg.genre"""

    sql2 = """
select distinct pr.title, cast((avg(cast(pr.rank as float))) as decimal(10,2))  as Average_Rank
from ProgramRanks pr, more_than_3_rates pwkr
where (pr.title = pwkr.title)
group by pr.title
order by Average_Rank DESC , pr.title asc
   """

    sql3 = """
    select distinct j.title
from join_by_title j
WHERE j.title not in(
        (SELECT distinct pr2.title
         FROM ProgramRanks pr2
         WHERE pr2.rank<2)
    )
order by j.title
"""
    with connection.cursor() as cursor:
        cursor.execute(sql1)
        sql1_res = dictfetchall(cursor)
        cursor.execute(sql2)
        sql2_res = dictfetchall(cursor)
        cursor.execute(sql3)
        sql3_res = dictfetchall(cursor)

    return render(request, 'Query_Results.html', {'sql1_res': sql1_res, 'sql2_res': sql2_res, 'sql3_res': sql3_res})


def Records_Management(request):
    with connection.cursor() as cursor:
        sql3 = """SELECT TOP 3 union_returns_orders.hID, COUNT(*) AS count
            FROM ((SELECT *
                   FROM RecordReturns rr)
                  UNION
                  (SELECT *
                   FROM RecordOrders ro)) AS union_returns_orders
            GROUP BY union_returns_orders.hID
            ORDER BY count DESC, union_returns_orders.hID ASC"""
        cursor.execute(sql3)
        sql_result = dictfetchall(cursor)
    if request.method == "POST" and request.POST:
        input_hid = request.POST["hID"]
        input_title = request.POST["title"]
        with connection.cursor() as cursor:
            cursor.execute("""select h.hID
                                from Households h
                                where h.hID=%s""", (input_hid,))
            result = dictfetchall(cursor)
            if len(result) == 0:
                flag = 1
                return render(request, 'Records_Management.html', {'flag': flag, 'sql_result': sql_result})
            else:
                cursor.execute("""select p.title
                                from Programs p
                                where p.title=%s""", (input_title,))
                result = dictfetchall(cursor)
                if len(result) == 0:
                    flag = 2
                    return render(request, 'Records_Management.html', {'flag': flag, 'sql_result': sql_result})
                else:
                    cursor.execute(
                        """ select ro.hID
                            from RecordOrders ro
                            where ro.hID=%s
                            group by ro.hID
                            having count(*)=3""",
                        (input_hid,))
                    result = dictfetchall(cursor)
                    if len(result) != 0:
                        flag = 3
                        return render(request, 'Records_Management.html', {'flag': flag, 'sql_result': sql_result})
                    else:
                        cursor.execute(""" select *
                                            from RecordOrders ro
                                            where ro.title=%s and ro.hID!=%s""""",
                                       (input_title, input_hid))
                        result = dictfetchall(cursor)
                        if len(result) != 0:
                            flag = 4
                            return render(request, 'Records_Management.html', {'flag': flag, 'sql_result': sql_result})
                        else:
                            cursor.execute(""" select *
                                                from RecordOrders ro
                                                where ro.title=%s and ro.hID=%s""",
                                           (input_title, input_hid))
                            result = dictfetchall(cursor)
                            if len(result) != 0:
                                flag = 5
                                return render(request, 'Records_Management.html',
                                              {'flag': flag, 'sql_result': sql_result})
                            else:
                                cursor.execute(""" select *
                                                from RecordReturns rr
                                                where rr.title=%s and rr.hID=%s""",
                                               (input_title, input_hid))
                                result = dictfetchall(cursor)
                                if len(result) != 0:
                                    flag = 6
                                    return render(request, 'Records_Management.html',
                                                  {'flag': flag, 'sql_result': sql_result})
                                else:
                                    cursor.execute(
                                        """ select *
                                        from Households h, Programs p
                                        where h.hID=%s and h.ChildrenNum>0 and p.title=%s and
                                              (p.genre='Reality' or p.genre='Adults only')""",
                                        (input_hid, input_title))
                                    result = dictfetchall(cursor)
                                    if len(result) != 0:
                                        flag = 7
                                        return render(request, 'Records_Management.html',
                                                      {'flag': flag, 'sql_result': sql_result})
                                    else:
                                        insert_sql = """Insert into RecordOrders (title, hID) values (%s, %s)"""
                                        cursor.execute(insert_sql, [input_title, input_hid])
    return render(request, 'Records_Management.html', {'sql_result': sql_result})


def return_a_order(request):
    with connection.cursor() as cursor:
        sql3 = """SELECT TOP 3 union_returns_orders.hID, COUNT(*) AS count
            FROM ((SELECT *
                   FROM RecordReturns rr)
                  UNION
                  (SELECT *
                   FROM RecordOrders ro)) AS union_returns_orders
            GROUP BY union_returns_orders.hID
            ORDER BY count DESC, union_returns_orders.hID ASC"""
        cursor.execute(sql3)
        sql_result = dictfetchall(cursor)
    flag2 = 0
    if request.method == "POST" and request.POST:
        input_hid = request.POST["hID"]
        input_title = request.POST["title"]
        with connection.cursor() as cursor:
            cursor.execute(""" select h.hID
                                from Households h
                                where h.hID=%s""", (input_hid,))
            result = dictfetchall(cursor)
            if len(result) == 0:
                flag2 = 1
                return render(request, 'Records_Management.html',
                              {'flag2': flag2, 'sql_result': sql_result})
            else:
                cursor.execute("""select *
                                    from Programs p, RecordOrders ro
                                    where p.title=%s and ro.hID=%s and ro.title=%s""",
                               (input_title, input_hid, input_title))
                result = dictfetchall(cursor)
                if len(result) == 0:
                    flag2 = 2
                    return render(request, 'Records_Management.html', {'flag2': flag2, 'sql_result': sql_result})
                else:
                    delete_from_orders_sql = """DELETE FROM RecordOrders where title = %s and hID = %s"""
                    cursor.execute(delete_from_orders_sql, [input_title, input_hid])
                    insert_to_returns_sql = """INSERT INTO RecordReturns (title, hID) values (%s, %s)"""
                    cursor.execute(insert_to_returns_sql, [input_title, input_hid])
    return render(request, 'Records_Management.html', {'sql_result': sql_result})


def top_3(request):
    with connection.cursor() as cursor:
        sql3 = """SELECT TOP 3 union_returns_orders.hID as hid, COUNT(*) as count
                    FROM ((SELECT *
                           FROM RecordReturns rr)
                          UNION
                          (SELECT *
                           FROM RecordOrders ro)) AS union_returns_orders
                    GROUP BY union_returns_orders.hID
                    ORDER BY count DESC, union_returns_orders.hID ASC"""
        cursor.execute(sql3)
        sql_result = dictfetchall(cursor)
    return render(request, 'Records_Management.html', {'sql_result': sql_result})


def Rankings(request):
    with connection.cursor() as cursor:
        cursor.execute("select h.hID from Households h")
        hid_list = dictfetchall(cursor)
        cursor.execute("select p.title from Programs p")
        program_list = dictfetchall(cursor)
        # spoken program
        cursor.execute("select p.genre from Programs p group by p.genre having count(p.title)>=5")
        genre_list = dictfetchall(cursor)

        if request.method == "POST" and request.POST:
            new_hid = request.POST.get("hID")
            new_title = request.POST.get("title")
            new_rank = request.POST.get("rank")
            # spoken program
            new_genre = request.POST.get("genre")
            new_minimum_rank = request.POST.get("min_rank")
            ###
            if new_rank and new_hid and new_title:
                cursor.execute("select * from ProgramRanks pr where pr.hID= %s and pr.title=%s", (new_hid, new_title))
                result = dictfetchall(cursor)
                if len(result) != 0:
                    rank_update = """UPDATE ProgramRanks SET hID=%s,title=%s , rank=%s WHERE hID= %s and title=%s"""
                    cursor.execute(rank_update, (new_hid, new_title, new_rank, new_hid, new_title))
                else:
                    rank_insert = """INSERT INTO ProgramRanks(title, hID, rank) values (%s,%s,%s)"""
                    cursor.execute(rank_insert, (new_title, new_hid, new_rank))

            # spoken programs
            elif new_genre and new_minimum_rank:
                spoken_program="""select TOP 5 pr.title, cast(avg(cast((pr.rank) as decimal)) as decimal(10,2)) as Average_Rank
                            from ProgramRanks pr, Programs p
                            where p.title=pr.title and p.genre=%s
                            group by pr.title
                            having count(*)>=%s
                            order by Average_Rank DESC """
                cursor.execute(spoken_program,(new_genre,new_minimum_rank))
                spoken_program_query_result = dictfetchall(cursor)
                if len(spoken_program_query_result) >= 5:
                    return render(request, 'Rankings.html', {'hid_list': hid_list, 'program_list': program_list,
                    'genre_list': genre_list,'spoken_program_query_result':spoken_program_query_result})
                # lower then 5
                else:
                    spoken_program_complete = """select top (5-%s) p.title, 0 as Average_Rank
                                            from Programs p
                                            where p.genre =%s and p.title not in(
                        select TOP 5 pr.title
                            from ProgramRanks pr, Programs p
                            where p.title=pr.title and p.genre=%s
                            group by pr.title
                            having count(*)>=%s
                                            )
                                            group by p.title
                                            order by p.title asc;"""
                    cursor.execute(spoken_program_complete,(len(spoken_program_query_result),new_genre,new_genre,new_minimum_rank))
                    spoken_program_complete_result = dictfetchall(cursor)
                    return render(request, 'Rankings.html', {'hid_list': hid_list, 'program_list': program_list,
                    'genre_list': genre_list,'spoken_program_query_result': spoken_program_query_result ,
                    'spoken_program_complete_result': spoken_program_complete_result})


    return render(request, 'Rankings.html',
                  {'hid_list': hid_list, 'program_list': program_list,'genre_list': genre_list})



