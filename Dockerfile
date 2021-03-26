FROM python:3.8-slim-buster

WORKDIR /my_nginx
COPY . /my_nginx

# VOLUME ["/var/www/html"]

CMD python3 App/server.py
EXPOSE 8080
#  sudo docker  build -t my_nginx .;
#  sudo docker run -p 80:80 --name my_nginx -t my_nginx;
#  curl -I http://0.0.0.0
 #s=$(docker ps -a | grep 'my_nginx' | cut -d ' ' -f 1);  docker kill $s;
 #sudo docker ps -a | grep  Exit| cut -d ' ' -f 1 | xargs  sudo docker rm;