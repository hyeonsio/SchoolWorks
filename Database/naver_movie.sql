create database naver_movie;
use naver_movie;

create user 'movie'@'%' identified by'movie';
grant all privileges on *.* to 'movie'@'%';

create table movie(
	mid int primary key,
    kor_title varchar(50),
	eng_title varchar(50),
    aud_rate float,
    aud_count int,
    net_rate float,
    net_count int,
    spc_rate float,
    spc_count int,
	rel_date datetime
);

create table genre(
	mid int,
    genre varchar(10),
	primary key(mid, genre),
    foreign key(mid) references movie(mid) 
);

create table nationality(
	mid int,
    nationality varchar(30),
	primary key(mid, nationality),
    foreign key(mid) references movie(mid) 
);

create table photo (
	mid int,
    photo  varchar(200),
	primary key(mid, photo),
    foreign key(mid) references movie(mid) 
);

create table video(
	mid int,
    video  varchar(200),
    title varchar(200),
	primary key(mid, video),
    foreign key(mid) references movie(mid) 
);

create table rating(
	mid int,
    rid int, 
	primary key(mid, rid),
    foreign key(mid) references movie(mid) ,
    
    rate int,
    content varchar(1000),
    nickname varchar(50),
	wr_date datetime,
    like_num int,
    dis_num int
);

create table review(
	mid int,
    rid int,
	primary key(rid),
    foreign key(mid) references movie(mid) ,

     title varchar(1000),
     wr_date datetime,
     view_num int,
     rec_num int
);

create table comments(
	rid int,
    cid int,
	primary key(rid, cid),
    foreign key(rid) references review(rid),
    txt varchar(1000),
    wr_date date
);

create table director(
	did int primary key,
    dname varchar(50)
);

create table actor(
	aid int primary key,
    aname varchar(50)
);


create table director_movie(
	mid int,
    did int,
	primary key(mid, did),
	foreign key(mid) references movie(mid) ,
	foreign key(did) references director(did)
);

create table actor_movie(
	mid int,
    aid int,
	primary key(mid, aid),
	foreign key(mid) references movie(mid) ,
	foreign key(aid) references actor(aid),
    rol varchar(50),
    casting varchar(50)
);

select count(*) as mvcount from movie;	
select count(*) as atcount from actor;	
select count(*) as drcount from director;
select count(*)as gcount from genre;	
select count(*) as pcount from photo;	
select count(*) as rvcount from review;	
select count(*) as rtcount from rating;	
select count(*) as drcount from director;	
select count(*) as amcount from actor_movie;	
select count(*) as dmcount from director_movie;	
select count(*) as vicount from video;	


select* from actor;
select* from director;
select* from review;
select* from rating;
select* from director;
select* from genre;
select* from nationality;
select* from movie;


create index idx_movie_ktitle on movie(kor_title);
create index idx_movie_etitle on movie(eng_title);
create index idx_movie_rdate on movie(rel_date);
create index idx_movie_nrate on movie(net_rate);
create index idx_dm_did on director_movie(did);
create index idx_dm_mid on director_movie(mid);
create index idx_am_aid on actor_movie(aid);
create index idx_am_mid on actor_movie(mid);
create index idx_dname on director(dname);
create index idx_aname on actor(aname);
create index idx_genre_mid on genre(mid);

