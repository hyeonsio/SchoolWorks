import pymysql
import os
import time
from collections import OrderedDict
from pymysql.cursors import DictCursorMixin, Cursor


def open_db():
    conn = pymysql.connect(host='localhost', user='movie',
                           password='movie', db='naver_movie')

    cur = conn.cursor(pymysql.cursors.DictCursor)
    return conn, cur


def close_db(conn, cur):
    cur.close()
    conn.close()


def front():
    search_result = []

    os.system('CLS')
    conn, cur = open_db()
    search_level = 0
    search_opt = 0
    sort_opt = 0
    search_input = ''
    search_way = ['영화 제목으로 검색', '배우 이름으로 검색', '감독 이름으로 검색', '장르로 검색']
    sort_way = ["가나다 순", "년도 순", "평점 순"]
    sort = ["kor_title", "rel_date", "net_rate"]
    mid = 0
    while True:
        print("─────────────────────────────────────────")
        print("    데이터베이스 과제 - 202011376 조현서     ")
        print("─────────────────────────────────────────")
        # 처음 화면 - 검색 방식 선택
        if search_level == 0:
            print("영화 검색\n")
            print("\t1. " + search_way[0])
            print("\t2. " + search_way[1])
            print("\t3. " + search_way[2])
            print("\t4. " + search_way[3])
            print("\t5. 종료")
            print("─────────────────────────────────────────")
            search_opt = int(input("영화 검색 옵션 : "))
            if 1 <= search_opt <= 4:
                search_level = 1
            elif search_opt == 5:
                break
            else:
                print("잘못된 입력입니다!")
                search_opt = 0
                time.sleep(2)
        # 두번 째 화면 검색어 입력
        elif search_level == 1:
            print(search_way[search_opt - 1])
            print("─────────────────────────────────────────")
            search_input = input('검색어를 입력해 주세요 : ')
            search_level = 2

        # 세번 째 화면 정렬방식 입력
        elif search_level == 2:
            print(search_way[search_opt - 1])
            print(f"검색어 : {search_input}\n")
            print("정렬 방식\n")
            print(f"\t1. {sort_way[0]}")
            print(f"\t2. {sort_way[1]}")
            print(f"\t3. {sort_way[2]}")
            print(f"\t4. 뒤로가기")
            print("─────────────────────────────────────────")
            sort_opt = int(input("정렬 옵션 : "))
            if 1 <= sort_opt <= 3:
                search_level = 3
            elif sort_opt == 4:
                search_level = 1
            else:
                print("잘못된 입력입니다!")
                time.sleep(2)

        # 검색 목록 화면 - 목록에서 원하는 정보 입력
        elif search_level == 3:
            if search_opt == 1:

                print(f"영화명 {search_input}에 대한 검색 결과")
                if sort_opt == 1:
                    sql = """
                        select kor_title,eng_title, rel_date, net_rate,mid
                        from movie
                        where kor_title like %s or eng_title like %s
                        order by kor_title
                    """
                elif sort_opt == 2:
                    sql = """
                        select kor_title,eng_title, rel_date, net_rate,mid
                        from movie
                        where kor_title like %s or eng_title like %s
                        order by rel_date
                    """
                else:
                    sql = """
                        select kor_title,eng_title, rel_date, net_rate,mid
                        from movie
                        where kor_title like %s or eng_title like %s
                        order by net_rate
                    """

                cur.execute(sql, (search_input + '%', search_input + '%'))
                row = cur.fetchone()
                while row:
                    search_result.append(
                        [row['kor_title'], row['eng_title'], row['rel_date'], row['net_rate'], row['mid']])
                    row = cur.fetchone()
            elif search_opt == 2:
                print(f"배우명 {search_input}에 대한 검색 결과")
                if sort_opt == 1:
                    sql = """
                        select kor_title, eng_title, rel_date, net_rate, m.mid
                        from movie m, actor a, actor_movie am
                        where m.mid = am.mid and a.aid = am.aid and a.aname like %s
                        order by kor_title
                    """
                elif sort_opt == 2:
                    sql = """
                        select kor_title, eng_title, rel_date, net_rate, m.mid
                        from movie m, actor a, actor_movie am
                        where m.mid = am.mid and a.aid = am.aid and a.aname like %s
                        order by rel_date
                    """
                else:
                    sql = """
                        select kor_title, eng_title, rel_date, net_rate, m.mid
                        from movie m, actor a, actor_movie am
                        where m.mid = am.mid and a.aid = am.aid and a.aname like %s
                        order by net_rate
                    """
                cur.execute(sql, (search_input + '%'))
                row = cur.fetchone()
                while row:
                    search_result.append(
                        [row['kor_title'], row['eng_title'], row['rel_date'], row['net_rate'], row['mid']])
                    row = cur.fetchone()

            elif search_opt == 3:
                print(f"감독명 {search_input}에 대한 검색 결과")
                if sort_opt == 1:
                    sql = """
                        select kor_title, eng_title, rel_date, net_rate, m.mid
                        from movie m, director d, director_movie dm
                        where m.mid = dm.mid and d.did = dm.did and d.dname like %s
                        order by kor_title
                    """
                elif sort_opt == 2:
                    sql = """
                        select kor_title, eng_title, rel_date, net_rate, m.mid
                        from movie m, director d, director_movie dm
                        where m.mid = dm.mid and d.did = dm.did and d.dname like %s
                        order by rel_date
                    """
                else:
                    sql = """
                        select kor_title, eng_title, rel_date, net_rate, m.mid
                        from movie m, director d, director_movie dm
                        where m.mid = dm.mid and d.did = dm.did and d.dname like %s
                        order by net_rate
                    """
                cur.execute(sql, (search_input + '%'))
                row = cur.fetchone()
                while row:
                    search_result.append(
                        [row['kor_title'], row['eng_title'], row['rel_date'], row['net_rate'], row['mid']])
                    row = cur.fetchone()
            else:
                print(f"장르 {search_input}에 대한 검색 결과")
                if sort_opt == 1:
                    sql = """
                        select kor_title, eng_title, rel_date, net_rate, m.mid
                        from movie m, genre g
                        where m.mid = g.mid and genre like %s
                        order by kor_title
                    """
                elif sort_opt == 2:
                    sql = """
                        select kor_title, eng_title, rel_date, net_rate, m.mid
                        from movie m, genre g
                        where m.mid = g.mid and genre like %s
                        order by rel_date
                    """
                else:
                    sql = """
                        select kor_title, eng_title, rel_date, net_rate, m.mid
                        from movie m, genre g
                        where m.mid = g.mid and genre like %s
                        order by net_rate
                    """
                cur.execute(sql, (search_input + '%'))
                row = cur.fetchone()
                while row:
                    search_result.append(
                        [row['kor_title'], row['eng_title'], row['rel_date'], row['net_rate'], row['mid']])
                    row = cur.fetchone()

            if len(search_result) == 0:
                print("\t검색 결과가 없습니다.")
                print("─────────────────────────────────────────")
                input("엔터키를 누르면 처음화면으로 돌아갑니다.")
                search_level = 0
                search_opt = 0
                sort_opt = 0
                search_input = ''
            else:
                print("\n\t\t한국제목\t영어제목\t출시년도\t평점\n")
                temp = 1
                for result in search_result:
                    if result[1] == '':
                        result[1] = '\t\t'
                    if len(result[0]) <= 3:
                        result[0] += '\t'
                    if type(result[2]) == str:
                        print(f"\t{temp}.\t{result[0]}\t{result[1]}\t{result[2][0:4]}\t{result[3]}")
                    else:
                        print(f"\t{temp}.\t{result[0]}\t{result[1]}\t{result[2].year}\t{result[3]}")
                    temp += 1
                print(f"\n\t정렬방식 : {sort_way[sort_opt - 1]}")
                print("─────────────────────────────────────────")
                mid = search_result[int(input("자세히 보고싶은 영화의 번호를 입력하세요 : ")) - 1][4]
                print(mid)
                search_level = 4
            search_result = []
        # 영화 정보 출력
        elif search_level == 4:
            print("영화 정보\n")
            sql = """
                select kor_title,eng_title, dname
                from movie m, director d, director_movie dm
                where m.mid = %s and m.mid = dm.mid and dm.did = d.did  
            """
            cur.execute(sql, mid)
            row = cur.fetchone()
            print("\t한국 제목 : " + row['kor_title'])
            print("\t영어 제목 : " + row['eng_title'])
            print("\t감독 : " + row['dname'], end='|')
            row = cur.fetchone()
            while row:
                print(row['dname'], end='|')
                row = cur.fetchone()
            print()
            ###
            sql = """
                select rol, casting, aname
                from movie m, actor a, actor_movie am
                where m.mid = %s and m.mid = am.mid and am.aid = a.aid  
            """
            cur.execute(sql, mid)
            row = cur.fetchone()
            print("\t출연\n"+"\t"+row['aname']+" :("+row['rol']+") "+row['rol']+"역")
            row = cur.fetchone()
            while row:
                print("\t"+row['aname']+" :("+row['rol']+") "+row['casting']+"역")
                row = cur.fetchone()
            print()
            ###
            sql = """
                select genre,aud_rate,aud_count,net_rate,net_count,spc_rate,spc_count
                from movie m, genre g
                where m.mid = %s and m.mid = g.mid 
            """
            cur.execute(sql, mid)
            row = cur.fetchone()
            print(f"\t관람객 수 :{row['aud_count']}  관람객 평점 :{row['aud_rate']}")
            print(f"\t네티즌 수 :{row['net_count']}  네티즌 평점 :{row['net_rate']}")
            print(f"\t전문가 수 :{row['spc_count']}  전문가 평점 :{row['spc_rate']}")
            print("\t장르 : " + row['genre'], end='|')
            row = cur.fetchone()
            while row:
                print(row['genre'], end='|')
                row = cur.fetchone()
            print("\n─────────────────────────────────────────")
            print("\n\t다음 번호를 누르면 상세 페이지로 이동합니다.")
            print("\t1. 사진")
            print("\t2. 동영상")
            print("\t3. 평점")
            print("\t4. 리뷰")
            print("\t5. 처음으로")
            print("─────────────────────────────────────────")
            spec = int(input("상세 페이지 번호 : "))
            if spec == 5:
                search_level = 0
                search_opt = 0
                sort_opt = 0
                search_input = ''
            else:
                search_level = 5
        else:
            if spec == 1:
                sql = """
                    select photo
                    from movie m, photo p
                    where m.mid = %s and m.mid = p.mid 
                """
                cur.execute(sql, mid)
                row = cur.fetchone()
                cnt = 1
                print("사진은 최대 5개까지 보여집니다.")
                while row:
                    print(f"\t{cnt}.   링크 : " + row['photo'])
                    if cnt > 5:
                        break
                    cnt += 1
                    row = cur.fetchone()
            elif spec == 2:
                sql = """
                    select video, title
                    from movie m, video v
                    where m.mid = %s and m.mid = v.mid 
                """
                cur.execute(sql, mid)
                row = cur.fetchone()
                cnt = 1
                print("영상 링크는 최대 5개까지 보여집니다.")
                while row:
                    print(f"\t{cnt}. 영상 제목 : " + row['title'] + ", 링크 : " + row['video'])
                    if cnt > 5:
                        break
                    cnt += 1
                    row = cur.fetchone()

            elif spec == 3:
                sql = """
                    select rid, rate, wr_date, like_num, dis_num, content
                    from movie m, rating r
                    where m.mid = %s and m.mid = r.mid 
                """
                cur.execute(sql, mid)
                row = cur.fetchone()
                while row:
                    print(
                        f"\t{row['rid'] + 1}. 평점 : {row['rate']} 작성일 : {row['wr_date']} 추천수 : {row['like_num']} 비추천수 : {row['dis_num']}")
                    print(f"\t내용 : {row['content']} \n")
                    row = cur.fetchone()
            else:
                sql = """
                    select rid, title, wr_date, view_num, rec_num
                    from movie m, review r
                    where m.mid = %s and m.mid = r.mid 
                """
                cur.execute(sql, mid)
                row = cur.fetchone()
                while row:
                    print(
                        f"\t{row['rid']}. 제목 : {row['title']} 작성일 : {row['wr_date']} 조회수 : {row['view_num']} 추천수 : {row['rec_num']}")
                    row = cur.fetchone()
            print("─────────────────────────────────────────")
            input("enter를 누르면 이전화면으로 돌아갑니다.")
            search_level = 4
        os.system('CLS')

    close_db(conn, cur)
    os.system('CLS')
    print("프로그램이 정상적으로 종료되었습니다.")


if __name__ == '__main__':
    front()
