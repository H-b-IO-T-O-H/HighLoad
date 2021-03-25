FROM python:3.8.5

WORKDIR /my_nginx
COPY ./App /my_nginx
COPY httpd.conf /etc/httpd.conf

EXPOSE 80
CMD python3 server.py