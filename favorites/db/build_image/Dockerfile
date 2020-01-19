FROM mysql:8.0
COPY init.sql /docker-entrypoint-initdb.d
EXPOSE 3306
ENV MYSQL_ROOT_PASSWORD pwdroot
ENV MYSQL_DATABASE favoritesdb
ENV MYSQL_USER favoritesdb_user
ENV MYSQL_PASSWORD favoritesdb_pwd
CMD ["mysqld","--secure-file-priv="]
ENTRYPOINT ["docker-entrypoint.sh"]
