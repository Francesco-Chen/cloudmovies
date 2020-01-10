create table if not exists movietable(
   budget int,
   genres varchar(2000),
   homepage varchar(200),
   id int primary key,
   keywords varchar(4000),
   original_language varchar(5),
   original_title varchar(200),
   overview varchar(2000),
   popularity double,
   production_companies varchar(2000),
   production_countries varchar(2000),
   release_date char(10),
   revenue bigint,
   runtime varchar(20),
   spoken_languages varchar(1000),
   status varchar(20),
   tagline varchar(2000),
   title varchar(200),
   vote_average double,
   vote_count int
   ) character set=utf8mb4;
   
   
LOAD DATA INFILE '/docker-entrypoint-initdb.d/data/tmdb_5000_movies.csv' 
INTO TABLE movietable
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
