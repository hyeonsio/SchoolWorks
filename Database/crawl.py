import pymysql
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

global movie_info
global genre_info
global nationality_info
global photo_info
global video_info
global rating_info
global review_info
global comments_info
global director_info
global actor_info
global director_movie_info
global actor_movie_info
global driver
global thumb_list


def open_db():
    conn = pymysql.connect(host='localhost', user='movie',
                           password='movie', db='naver_movie')

    cur = conn.cursor(pymysql.cursors.DictCursor)

    return conn, cur


def close_db(conn, cur):
    cur.close()
    conn.close()


def crawl(mid, soup, page_num=1):
    global movie_info
    global genre_info
    global nationality_info
    global photo_info
    global video_info
    global rating_info
    global review_info
    global comments_info
    global director_info
    global actor_info
    global director_movie_info
    global actor_movie_info
    global driver
    global thumb_list

    # 크롤링해서 넣기
    #############################################################################
    # 1. 영화
    # mid, 한국 영어 제목

    mid = mid
    kor_title = soup.select_one("div.mv_info_area > div.mv_info > h3 > a")
    if kor_title is not None:
        kor_title = kor_title.text

    eng_title = soup.select_one("div.mv_info_area > div.mv_info > strong")
    if eng_title is not None:
        eng_title = eng_title.text[0:-6]
    # 관람객 평점
    audience_ = soup.select("a#actualPointPersentWide > div.star_score > em")
    audience_rate = ''
    for e in audience_:
        audience_rate += e.text
    if audience_rate == '':
        audience_rate = 0.00

    audience_count = soup.select_one("div#actualPointCountWide > em")
    if audience_count is not None:
        audience_count = audience_count.text
        audience_count = audience_count.replace(",", "")
    else:
        audience_count = 0

    # 네티즌 평점
    netizen_ = soup.select("a#pointNetizenPersentWide > em")
    netizen_rate = ''
    for e in netizen_:
        netizen_rate += e.text
    if netizen_rate == '':
        netizen_rate = 0.00

    netizen_count = soup.select_one("div#pointNetizenCountBasic > em")
    if netizen_count is not None:
        netizen_count = netizen_count.text
        netizen_count = netizen_count.replace(",", "")
    else:
        netizen_count = 0

    # 전문가 평점
    specialist_ = soup.select("div.special_score > div.sc_view > div.star_score > em")
    specialist_rate = ''
    for e in specialist_:
        specialist_rate += e.text
    if specialist_ is None:
        specialist_rate = 0.00
    specialist_count = soup.select_one("div.special_score > div.sc_view > span > em")
    if specialist_count is not None:
        specialist_count = specialist_count.text
        specialist_count = specialist_count.replace(",", "")
    else:
        specialist_count = 0
    # 개봉일
    rel_ = soup.select("dl.info_spec > dd > p > span:nth-child(4) > a")
    rel_date = ''
    for e in rel_:
        rel_date += e.text
    movie_info.append((mid, kor_title, eng_title, audience_rate, audience_count, netizen_rate, netizen_count,
                       specialist_rate, specialist_count, rel_date.strip()))

    #############################################################################
    # 2. 장르
    genre_ = soup.select("dl.info_spec > dd > p > span:nth-child(1) > a")
    for e in genre_:
        genre_info.append((mid, e.text))

    #############################################################################
    # 3. 국적
    nation_ = soup.select("dl.info_spec > dd > p > span:nth-child(2) > a")
    for e in nation_:
        nationality_info.append((mid, e.text))

    #############################################################################
    # 4. 배우 감독
    reqa = requests.get("https://movie.naver.com/movie/bi/mi/detail.naver?code=" + str(mid))
    soupa = BeautifulSoup(reqa.text, "html.parser")
    actor_ = soupa.select("ul.lst_people > li > div.p_info > a")
    idx = 1
    for e in actor_:
        # id
        aid = e.attrs["href"][e.attrs["href"].find('=') + 1::]
        # 이름
        aname = e.text
        actor_info.append((aid, aname))
        # 주조연
        rol = soupa.select_one(
            "ul.lst_people > li:nth-child(" + str(idx) + ") > div.p_info > div.part > p.in_prt > em")
        if rol is not None:
            rol = rol.text
        # 배역
        casting = soupa.select_one(
            "ul.lst_people > li:nth-child(" + str(idx) + ") >  div.p_info > div.part > p.pe_cmt > span")
        if casting is not None:
            casting = casting.text[0:-2]

        actor_movie_info.append((mid, aid, rol, casting))

        idx += 1

    dname_ = soupa.select_one("div.info_spec2 > dl.step1 > dd >a")
    if dname_ is not None:
        dname = dname_.text
        did = dname_.attrs["href"][dname_.attrs["href"].find('=') + 1::]
        director_info.append((did, dname))
        director_movie_info.append((mid, did))

    #############################################################################
    # 5. 사진
    reqp = requests.get("https://movie.naver.com/movie/bi/mi/photoView.naver?code=" + str(mid))
    soupp = BeautifulSoup(reqp.text, "html.parser")
    photo_ = soupp.select("div.rolling_list > ul > li._list > a> img")
    for e in photo_:
        psrc = e['src']
        photo_info.append((mid, psrc))

    #############################################################################
    # 6. 동영상
    reqv = requests.get("https://movie.naver.com/movie/bi/mi/media.naver?code=" + str(mid))
    soupv = BeautifulSoup(reqv.text, "html.parser")
    vrt = "https://movie.naver.com"
    video_ = soupv.select("ul.video_thumb > li > p > a")
    for e in video_:
        vsrc = vrt + e.attrs["href"]
        vtitle = e.text
        video_info.append((mid, vsrc, vtitle))

    #############################################################################
    # 7. 평점 - 링크를 바꿔야 함. 첫 페이지만
    reqrt = requests.get("https://movie.naver.com/movie/bi/mi/pointWriteFormList.naver?code=" + str(
        mid) + "&type=after&isActualPointWriteExecute=false&isMileageSubscriptionAlready=false&isMileageSubscriptionReject=false")
    souprt = BeautifulSoup(reqrt.text, "html.parser")

    ratid = 0
    rate_ = souprt.select("div.score_result > ul > li >div.star_score")
    nickname_ = souprt.select("div.score_result > ul > li >div.score_reple > dl > dt > em > a > span")
    wr_date_ = souprt.select("div.score_result > ul > li >div.score_reple > dl > dt > em:nth-child(2)")
    like_num_ = souprt.select("div.score_result > ul > li >div.btn_area >a._sympathyButton > strong")
    dis_num_ = souprt.select("div.score_result > ul > li >div.btn_area >a._notSympathyButton > strong")
    for e in rate_:
        try:
            rate = e.text.strip()
            content = souprt.select_one(
                "div.score_result > ul > li >div.score_reple > p > span#_filtered_ment_" + str(ratid)).text.strip()
            nickname = nickname_[ratid].text.strip()
            wr_date = wr_date_[ratid].text[0:-6].strip()
            like_num = like_num_[ratid].text.strip()
            dis_num = dis_num_[ratid].text.strip()
            rating_info.append((mid, ratid, rate, content, nickname, wr_date, like_num, dis_num))
            ratid += 1
        except:
            pass

    #############################################################################
    # 8. 리뷰, 댓글 review base 동적
    reqrvb = requests.get("https://movie.naver.com/movie/bi/mi/review.naver?code=" + str(mid))
    souprvb = BeautifulSoup(reqrvb.text, "html.parser")
    rvid_list_ = souprvb.select("ul.rvw_list_area > li > a")
    rvid_list = []  # 리뷰 id 리스트
    for e in rvid_list_:
        rvid_list.append(e.attrs['onclick'][-8:-1])

    for rvid in rvid_list:
        referer = "https://movie.naver.com/movie/bi/mi/reviewread.naver?nid=" + str(rvid) + "&code=" + str(
            mid) + "&order=#tab"
        reqrv = requests.get(referer)
        souprv = BeautifulSoup(reqrv.text, "html.parser")
        # mid rid title wrdate viewnum recnum comments
        rvtitle = souprv.select_one("div.top_behavior > strong")
        if rvtitle is None:
            continue
        rvtitle = rvtitle.text
        wr_date = souprv.select_one("div.top_behavior > span").text
        view_num = souprv.select_one("div.user_tx_info > span > em").text
        rec_num = souprv.select_one("div.user_tx_info > span > em#goodReviewCount").text
        review_info.append((mid, rvid, rvtitle, wr_date, view_num, rec_num))
        driver.get(referer)
        cid = 0
        txt_ = driver.find_elements_by_css_selector('div.u_cbox_area > u.cbox_text_wrap > span')
        wr_date_ = driver.find_elements_by_css_selector('div.u_cbox_area > > u.cbox_info_base > span.u_cbox_date')
        for txt in txt_:
            comments_info.append((rvid, cid, txt, wr_date_[cid]))
            cid += 1
    # 각각의 영화 별 관련 영화 추가. t_code mid 분리 이유 : 프로그램 영원히 안끝남.
    if page_num == 1:
        thumb_list = soup.select('ul.thumb_link_mv > li > a')
        del thumb_list[1::2]  # 중복 삭제 (홀수 index 삭제)


def gen_movie_list():
    conn, cur = open_db()
    global movie_info
    global genre_info
    global nationality_info
    global photo_info
    global video_info
    global rating_info
    global review_info
    global comments_info
    global director_info
    global actor_info
    global director_movie_info
    global actor_movie_info
    global driver
    global thumb_list
    driver = webdriver.Chrome('c:/chromedriver.exe')
    movie_info = []
    genre_info = []
    nationality_info = []
    photo_info = []
    video_info = []
    rating_info = []
    review_info = []
    comments_info = []
    director_info = []
    actor_info = []
    director_movie_info = []
    actor_movie_info = []

    # 인기 순 페이지 page_num, page 당 50개 영화, 영화 당 5개 총 300 movie/page. 300 * 40 = 12000
    for page_num in range(1, 41):  # 41로 바꿀 것

        # page 별 movie code crawl // request c - code, b - basic,
        reqc = requests.get(
            'https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=pnt&date=20220609&page=' + str(page_num))
        soupc = BeautifulSoup(reqc.text, "html.parser")
        movie_list = soupc.select('div.tit5 > a')
        mid_list = []

        for e in movie_list:
            mid_list.append(e.attrs["href"][e.attrs["href"].find('=') + 1::])  # href 에서 code = 부분 만 추출

        # 각각의 영화 페이지 1
        mvidx = 1
        for mid in mid_list:
            print(f"{page_num}pg {mvidx}th mv")
            mvidx += 1
            reqb = requests.get("https://movie.naver.com/movie/bi/mi/basic.naver?code=" + str(mid))
            soapb = BeautifulSoup(reqb.text, "html.parser")
            crawl(mid, soapb)

            t_code_list = []

            for e in thumb_list:
                t_code_list.append(e.attrs["href"][e.attrs["href"].find('=') + 1::])

            # 각각의 영화 페이지 - 관련 영화 2
            for t_code in t_code_list:
                req3 = requests.get("https://movie.naver.com/movie/bi/mi/basic.naver?code=" + str(t_code))
                soup3 = BeautifulSoup(req3.text, "html.parser")
                crawl(t_code, soup3, 2)

        try:
            print("movie insert start")

            insert_sql1 = """insert ignore into movie(mid, kor_title, eng_title, aud_rate, aud_count, net_rate, net_count, spc_rate, spc_count, rel_date)
                            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            insert_sql2 = """insert ignore into genre(mid, genre) values(%s, %s)"""
            insert_sql3 = """insert ignore into nationality(mid, nationality) values(%s, %s)"""
            insert_sql4 = """insert ignore into photo(mid, photo) values(%s, %s)"""
            insert_sql5 = """insert ignore into video(mid,video,title) values(%s, %s, %s)"""
            insert_sql6 = """insert ignore into rating(mid, rid,rate, content, nickname, wr_date, like_num,dis_num)
             values(%s, %s,%s, %s,%s, %s,%s, %s)"""
            insert_sql7 = """insert ignore into review(mid, rid, title,  wr_date, view_num,rec_num ) values(%s, %s,%s, %s, %s,%s)"""
            insert_sql8 = """insert into comments(rid, cid,txt,wr_date) values(%s, %s,%s,%s)"""
            insert_sql9 = """insert ignore into director(did, dname) values(%s, %s)"""
            insert_sql10 = """insert ignore into actor(aid, aname) values(%s, %s)"""
            insert_sql11 = """insert ignore into director_movie(mid, did) values(%s, %s)"""
            insert_sql12 = """insert ignore into actor_movie(mid, aid, rol,casting) values(%s, %s, %s,%s)"""

            cur.executemany(insert_sql1, movie_info)
            cur.executemany(insert_sql2, genre_info)
            cur.executemany(insert_sql3, nationality_info)
            cur.executemany(insert_sql4, photo_info)
            cur.executemany(insert_sql5, video_info)
            cur.executemany(insert_sql6, rating_info)
            cur.executemany(insert_sql7, review_info)
            cur.executemany(insert_sql8, comments_info)
            cur.executemany(insert_sql9, director_info)
            cur.executemany(insert_sql10, actor_info)
            cur.executemany(insert_sql11, director_movie_info)
            cur.executemany(insert_sql12, actor_movie_info)
            conn.commit()
            movie_info = []
            genre_info = []
            nationality_info = []
            photo_info = []
            video_info = []
            rating_info = []
            review_info = []
            comments_info = []
            director_info = []
            actor_info = []
            director_movie_info = []
            actor_movie_info = []
            print(f"{page_num} insert success")
        except:
            print(f"{page_num} insert filed")
            pass

    # 한국 영화 페이지
    mid_list = []
    for page_num in range(1, 1850):
        req1 = requests.get(
            'https://movie.naver.com/movie/sdb/browsing/bmovie.naver?nation=KR&page=' + str(page_num))
        soup1 = BeautifulSoup(req1.text, "html.parser")
        movie_list = soup1.select('ul.directory_list > li > a')

        # 각각의 영화 페이지
        for e in movie_list:
            mid_list.append(e.attrs["href"][e.attrs["href"].find('=') + 1::])
        mvidx = 1
        for mid in mid_list:
            print(f"kor {page_num}pg {mvidx}th mv")
            mvidx += 1
            req2 = requests.get("https://movie.naver.com/movie/bi/mi/basic.naver?code=" + str(mid))
            soup2 = BeautifulSoup(req2.text, "html.parser")
            crawl(mid, soup2)
        try:
            print("movie insert start")

            insert_sql1 = """insert ignore into movie(mid, kor_title, eng_title, aud_rate, aud_count, net_rate, net_count, spc_rate, spc_count, rel_date)
                            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            insert_sql2 = """insert ignore into genre(mid, genre) values(%s, %s)"""

            insert_sql3 = """insert ignore into nationality(mid, nationality) values(%s, %s)"""
            insert_sql4 = """insert ignore into photo(mid, photo) values(%s, %s)"""
            insert_sql5 = """insert ignore into video(mid,video,title) values(%s, %s, %s)"""
            insert_sql6 = """insert ignore into rating(mid, rid,rate, content, nickname, wr_date, like_num,dis_num)
             values(%s, %s,%s, %s,%s, %s,%s, %s)"""

            insert_sql7 = """insert ignore into review(mid, rid, title,  wr_date, view_num,rec_num ) values(%s, %s,%s, %s, %s,%s)"""
            insert_sql8 = """insert into comments(rid, cid,txt,wr_date) values(%s, %s, %s,%s)"""

            insert_sql9 = """insert ignore into director(did, dname) values(%s, %s)"""
            insert_sql10 = """insert ignore into actor(aid, aname) values(%s, %s)"""
            insert_sql11 = """insert ignore into director_movie(mid, did) values(%s, %s)"""
            insert_sql12 = """insert ignore into actor_movie(mid, aid, rol,casting) values(%s, %s, %s,%s)"""
            cur.executemany(insert_sql1, movie_info)
            cur.executemany(insert_sql2, genre_info)
            cur.executemany(insert_sql3, nationality_info)
            cur.executemany(insert_sql4, photo_info)
            cur.executemany(insert_sql5, video_info)
            cur.executemany(insert_sql6, rating_info)
            cur.executemany(insert_sql7, review_info)
            cur.executemany(insert_sql8, comments_info)
            cur.executemany(insert_sql9, director_info)
            cur.executemany(insert_sql10, actor_info)
            cur.executemany(insert_sql11, director_movie_info)
            cur.executemany(insert_sql12, actor_movie_info)
            conn.commit()
            movie_info = []
            genre_info = []
            nationality_info = []
            photo_info = []
            video_info = []
            rating_info = []
            review_info = []
            comments_info = []
            director_info = []
            actor_info = []
            director_movie_info = []
            actor_movie_info = []
            print("movie insert success")
            mid_list = []
        except:
            print("movie insert fail")
            pass
    close_db(conn, cur)


if __name__ == '__main__':
    gen_movie_list()
