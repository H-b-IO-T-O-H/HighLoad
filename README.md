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

![Иллюстрация к проекту](https://raw.githubusercontent.com/H-b-IO-T-O-H/HighLoad/dz2/benchmarks/wrk_small_file.png)
- get big russian_wikipedia.html file:
![Иллюстрация к проекту](https://raw.githubusercontent.com/H-b-IO-T-O-H/HighLoad/dz2/benchmarks/ab_wiki.png)
- compare 1 cpu vs 8 cpu 
![Иллюстрация к проекту](https://raw.githubusercontent.com/H-b-IO-T-O-H/HighLoad/dz2/benchmarks/wrk_30sec_wiki.png)
