FROM mysql:8.0
COPY init.sql /docker-entrypoint-initdb.d
EXPOSE 3306
ENV MYSQL_ROOT_PASSWORD pwdroot
ENV MYSQL_DATABASE userdb
ENV MYSQL_USER userdb_user
ENV MYSQL_PASSWORD userdb_pwd
CMD ["mysqld","--secure-file-priv="]
ENTRYPOINT ["docker-entrypoint.sh"]
