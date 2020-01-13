create table users(
  id int not null AUTO_INCREMENT primary key,
  username varchar(30) not null,
  pwd varchar(72) not null,
  role varchar(10) not null
);

insert into users (username, pwd, role) 
values(
  'admin',
  '$2b$10$wV53zulfzA7RLfKPSFsZUOcmPGMnOnxlMLfFjh9DzstV3HRuNKSxO',
  'admin'
);

create table favorites (
  userid int,
  movieid int,
  created datetime,
  primary key (userid,movieid)
);
