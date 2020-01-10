FROM mysql:8.0
RUN mkdir /docker-entrypoint-initdb.d/data
COPY init/init.sql /docker-entrypoint-initdb.d
COPY init/data/tmdb_5000_movies.csv /docker-entrypoint-initdb.d/data
EXPOSE 3306
ENV MYSQL_ROOT_PASSWORD pwdroot
ENV MYSQL_DATABASE movie_db
ENV MYSQL_USER movie_db_user
ENV MYSQL_PASSWORD movie_db_pwd
CMD ["mysqld","--secure-file-priv="]
ENTRYPOINT ["docker-entrypoint.sh"]
