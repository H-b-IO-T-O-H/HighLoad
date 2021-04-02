import socket
import sys
from worker import *
from config import config_reader
from logger import log


class Server:
    def __init__(self):
        self.logger = log
        self.config = config_reader('httpd.conf', self.logger)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # ipv4 потоковый сокет, работает по протоколу TCP
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # обновляет сокет, не дожидаясь дефолтного таймаута
        try:
            sock.bind((self.config['host'], self.config['port']))  # привязка сокета к хосту и порту
        except OSError:
            log.error(f'another app running on your address')
            sys.exit(1)
        sock.listen(self.config['parallel_conn'])  # кол-во одновременных соединений
        sock.setblocking(False)  # Resource temporarily unavailable error instead of waiting for data/socket.

        self.socket = sock

    def run(self):
        cpu_count = self.config['cpu_count']
        self.logger.info(f"start {cpu_count} workers on {self.config['port']} port...")
        workers = []
        for _ in range(cpu_count):
            w = Worker(self.socket, self.config)
            workers.append(w)
            w.start()

        try:
            for w in workers:
                w.join()
        except KeyboardInterrupt:
            for w in workers:
                w.terminate()
        finally:
            self.socket.close()


if __name__ == '__main__':
    server = Server()
    server.run()
