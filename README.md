# HighLoad DZ2

The project was developed as part of the Technopark's high-load systems course.

### Используемая архитектура:
prefork(via multiprocessing)+polling?(via asyncio)

### benchmarks:
- get a small index.html file:
    - 2 cpu;
    - 4 cpu;
    - 8 cpu;
    - 8 cpu nginx;
  
### Run:
`
sudo docker  build -t my_nginx .;
sudo docker run -p 80:80 --name my_nginx -t my_nginx;
`

### Stop:
`
s=$(docker ps -a | grep 'my_nginx' | cut -d ' ' -f 1);  docker kill $s;
sudo docker ps -a | grep  Exit| cut -d ' ' -f 1 | xargs  sudo docker rm;
`

### Func Tests for an app in a docker:
`
  cd http-test-suite;
  python3 ./httptest.py
`

### Tests for /var/www/html dir:
`
  ab -n 10000 -c 100 http://0.0.0.0:8080/wikipedia_russia.html;
  wrk -t12 -c400 -d10s http://0.0.0.0:8080/wikipedia_russia.html;
`

![Иллюстрация к проекту](https://raw.githubusercontent.com/H-b-IO-T-O-H/HighLoad/dz2/benchmarks/wrk_small_file.png)
- get big russian_wikipedia.html file:
![Иллюстрация к проекту](https://raw.githubusercontent.com/H-b-IO-T-O-H/HighLoad/dz2/benchmarks/ab_wiki.png)
- compare 1 cpu vs 8 cpu 
![Иллюстрация к проекту](https://raw.githubusercontent.com/H-b-IO-T-O-H/HighLoad/dz2/benchmarks/wrk_30sec_wiki.png)
