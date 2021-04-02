import multiprocessing
import asyncio
from response import HttpResponse


class Worker(multiprocessing.Process):
    def __init__(self, sock, config):
        super(Worker, self).__init__()
        self.sock = sock
        self.loop = None
        self.config = config

    def run(self):
        self.loop = asyncio.new_event_loop()
        try:
            self.loop.run_until_complete(self.work())
        except KeyboardInterrupt:
            print('shutdown worker.')
            self.loop.close()

    async def work(self):
        timeout = self.config['conn_timeout']
        while True:
            conn, _ = await self.loop.sock_accept(self.sock)
            conn.settimeout(timeout)
            conn.setblocking(False)
            await self.handle_connection(conn)
            conn.close()

    async def handle_connection(self, conn):
        data = await self.loop.sock_recv(conn, 1024)
        data = data.splitlines()
        if not data:
            return
        first_line = data[0].split()
        if len(first_line) < 2:
            return

        method_str = first_line[0].decode('utf-8')
        path_str = first_line[1].decode('utf-8')

        resp = HttpResponse(method_str, path_str, self.config['document_dir'])
        headers = resp.get_headers()

        await self.loop.sock_sendall(conn, headers)
        if resp.has_file:
            try:
                with open(resp.filename, 'rb') as f:
                    await self.loop.sock_sendall(conn, f.read())
            except IOError:
                pass
