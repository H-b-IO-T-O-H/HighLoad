import multiprocessing
import asyncio

from App.utils import HttpResponse

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'


class Worker(multiprocessing.Process):
    def __init__(self, sock, config):
        super(Worker, self).__init__()
        self.sock = sock
        self.loop = None
        self.config = config

    def run(self):
        self.loop = asyncio.get_event_loop()

        try:
            self.loop.run_until_complete(self.work())
        except KeyboardInterrupt as e:
            print("Caught keyboard interrupt. Canceling tasks...")
        finally:
            print('Successfully shutdown worker.')
            self.loop.close()

    async def work(self):
        while True:
            conn, _ = await self.loop.sock_accept(self.sock)
            conn.settimeout(self.config['conn_timeout'])
            conn.setblocking(False)
            self.loop.create_task(self.handle_conn(conn))

    async def handle_conn(self, conn):

        loop = asyncio.get_event_loop()
        data = b''
        while EOL1 not in data and EOL2 not in data:
            data_buffer = (await self.loop.sock_recv(conn, 1024))
            if not data_buffer:
                break
            data += data_buffer
        data = data.splitlines()
        if not data:
            return
        first_line = data[0].split()
        if len(first_line) < 2:
            return

        method_str = first_line[0].decode('utf-8')
        path_str = first_line[1].decode('utf-8')

        response = HttpResponse(method_str, path_str, self.config['document_dir']).to_str()
        await loop.sock_sendall(conn, response)
        conn.close()
