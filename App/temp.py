import getopt
import os
import socket
import sys
import multiprocessing as mp
import select
from logger import log
from utils import HttpResponse

HOST = 'localhost'
PORT = 8080
EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
TIMEOUT = 1.0

log_flag = False
cpu_count = mp.cpu_count()
document_dir = './DOCUMENT_ROOT'


def child(sock):
    while True:
        try:
            connection_socket, address = sock.accept()
            data = b''
            ready = select.select([connection_socket], [], [], TIMEOUT)
            if not ready[0]:
                continue

            while EOL1 not in data and EOL2 not in data:
                data_buffer = connection_socket.recv(1024)
                if not data_buffer:
                    break
                data += data_buffer

            data = data.splitlines()
            if not data:
                continue
            first_line = data[0].split()
            if len(first_line) < 2:
                continue

            method_str = first_line[0].decode('utf-8')
            path_str = first_line[1].decode('utf-8')

            response = HttpResponse(method_str, path_str, document_dir).to_str()
            bytes_sent_total = 0
            while bytes_sent_total < len(response):
                data_to_send = response[bytes_sent_total:]
                temp = connection_socket.send(data_to_send)
                bytes_sent_total += temp

            connection_socket.close()
        except KeyboardInterrupt:
            return
        except socket.timeout:
            print("timeout exception")
            continue
        except socket.error:
            #print("error exception")
            continue


def print_help():
    print("-r DOCUMENT_DIR  set relative document directory")
    print("-c CPU_COUNT     set CPU count")
    print("-l               get log output")
    print("-h               show help")


class Server:
    def __init__(self):
        self.logger = log
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        sock.setblocking(False)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.socket = sock

    def run(self):
        self.socket.listen(socket.SOMAXCONN)
        #child(self.socket)

        workers = [mp.Process(target=child, args=(self.socket,), name="Worker " + str(i + 1)) for i in range(cpu_count)]
        for p in workers:
            self.logger.info(f"Started process {p}")
            p.start()


if __name__ == '__main__':
    print(cpu_count)
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'r:c:lh')
    except getopt.GetoptError:
        print_help()
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-r':
            document_dir = arg
        elif opt == '-c':
            try:
                cpu_count = int(arg)
            except ValueError:
                print_help()
                sys.exit(2)
        elif opt == '-l':
            log_flag = True
        elif opt == '-h':
            print_help()
            sys.exit(0)

    server = Server()
    server.run()

    # for process in multiprocessing.active_children():
    #     process.terminate()
    #     process.join()
