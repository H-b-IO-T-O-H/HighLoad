from datetime import datetime
from urllib.parse import unquote
import os.path

# file:////home/vlad/HighLoad/http-test-suite/httptest/wikipedia_russia.html
# http://localhost/httptest/wikipedia_russia.html
# /var/www/html
# /home/vlad/HighLoad/http-test-suite
# /home/vlad/HighLoad/http-test-suite

STATUS_OK = '200 OK'
STATUS_FORBIDDEN = '403 Forbidden'
STATUS_NOT_FOUND = '404 Not Found'
STATUS_METHOD_NOT_ALLOWED = '405 Method Not Allowed'


class HttpResponse:
    def __init__(self, method_str, path_str, document_dir):
        self.method = method_str
        self.document_dir = document_dir
        self.filename = ''
        self.has_file = False
        self.content_len = ''
        self.status = STATUS_OK
        self.date = datetime.now().strftime('Date: %a, %d %b %Y %H:%M:%S GMT +3')
        self.server = 'Server: python-server (Unix)'
        self.connection = 'Connection: close'

        self.create_response(path_str)

    def create_response(self, path_str):
        self.filename = self.document_dir + path_str
        if self.filename.endswith('/') and not ('.html' in path_str):
            self.filename += 'index.html'
            if not os.path.isfile(self.filename):
                self.status = STATUS_FORBIDDEN
                return

        self.filename = unquote(self.filename)
        if '?' in self.filename:
            self.filename = self.filename.split('?')[0]

        if self.method != 'GET' and self.method != 'HEAD':
            self.status = STATUS_METHOD_NOT_ALLOWED
            return

        if not os.path.isfile(self.filename):
            self.status = STATUS_NOT_FOUND
            return

        if '..' in path_str:
            found = False
            name = self.filename.rsplit('/', 1)[1]
            for _, _, files in os.walk(self.document_dir):
                if name in files:
                    found = True
                    break
            if not found:
                self.status = STATUS_FORBIDDEN
                return
        self.status = STATUS_OK
        with open(self.filename, 'rb') as _:
            self.content_len = str(os.path.getsize(self.filename))
        if self.method != 'HEAD':
            self.has_file = True

    def get_headers(self):
        res = f'HTTP/1.1 {self.status}\r\n'
        res += f'{self.date}\r\n'
        res += f'{self.server}\r\n'
        res += f'{self.connection}\r\n'
        if self.filename:
            res += f'Content-Type: {self.get_content_type()}\r\n'
            res += f'Content-Length: {self.content_len}\r\n'
            res += '\r\n'

        return bytes(res, 'utf8')

    def get_content_type(self):
        # content_type = mimetypes.guess_type(self.filename)[0]
        if self.filename.lower().endswith('.html') or self.status == STATUS_NOT_FOUND:
            content_type = 'text/html'
        elif self.filename.lower().endswith('.css'):
            content_type = 'text/css'
        elif self.filename.lower().endswith('.js'):
            content_type = 'application/javascript'
        elif self.filename.lower().endswith('.jpg') or self.filename.lower().endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif self.filename.lower().endswith('.png'):
            content_type = 'image/png'
        elif self.filename.lower().endswith('.gif'):
            content_type = 'image/gif'
        elif self.filename.lower().endswith('.swf'):
            content_type = 'application/x-shockwave-flash'
        else:
            content_type = 'text/plain'

        return content_type
