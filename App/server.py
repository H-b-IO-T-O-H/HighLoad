#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getopt
import socket
import sys
import multiprocessing
import select
from multiprocessing import Process
from utils import HttpResponse

HOST = '127.0.0.1'
PORT = 8080
EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
TIMEOUT = 1.0

log_flag = False
cpu_count = multiprocessing.cpu_count()
document_dir = './DOCUMENT_ROOT'


def child(server):
    while True:
        try:
            connection_socket, address = server.accept()
            data = b''
            ready = select.select([connection_socket], [], [], TIMEOUT)
            if not ready[0]:
                continue

            while EOL1 not in data and EOL2 not in data:
                data_buffer = connection_socket.recv(1024)
                if not data_buffer:
                    break
                data += data_buffer

            # if log_flag:
            #     print(data)

            data = data.splitlines()
            if not data:
                continue
            first_line = data[0].split()
            if len(first_line) < 2:
                continue
            if log_flag:
                print(first_line)

            method_str = first_line[0].decode('utf-8')
            path_str = first_line[1].decode('utf-8')

            response = HttpResponse(method_str, path_str, document_dir).to_str()
            bytes_sent_total = 0
            while bytes_sent_total < len(response):
                data_to_send = response[bytes_sent_total:].encode('utf-8')
                temp = connection_socket.send(data_to_send)
                bytes_sent_total += temp

            connection_socket.close()
        except KeyboardInterrupt:
            return
        except socket.timeout:
            print("timeout exception")
            continue
        except socket.error:
            print("error exception")
            continue


def print_help():
    print("-r DOCUMENT_DIR  set relative document directory")
    print("-c CPU_COUNT     set CPU count")
    print("-l               get log output")
    print("-h               show help")


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "r:c:lh")
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

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.settimeout(TIMEOUT)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((HOST, PORT))
    except socket.error as e:
        print(e.args[1])
        sys.exit(1)

    server_socket.listen(socket.SOMAXCONN)
    child(server_socket)

    # if log_flag:
    #     print('Server started on %s:%s' % (HOST, str(PORT)))
    #     print('Uses %s CPUs' % cpu_count)

    # for i in range(cpu_count):
    # proc = Process(target=child, args=(server_socket,), name="Worker " + str(1))
    # proc.start()
    # if log_flag:
    #     print("Process %s started, pid %s" % (1, proc.pid))
