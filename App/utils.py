#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
from datetime import datetime
from urllib.parse import unquote
import os.path

from PIL import Image

# file:////home/vlad/HighLoad/http-test-suite/httptest/wikipedia_russia.html
# http://localhost/httptest/wikipedia_russia.html

STATUS_OK = b'200 OK'
STATUS_FORBIDDEN = b'403 Forbidden'
STATUS_NOT_FOUND = b'404 Not Found'
STATUS_METHOD_NOT_ALLOWED = b'405 Method Not Allowed'
EOL3 = b'\r\n'


class HttpResponse:
    def __init__(self, method_str, path_str, document_dir):
        self.method = method_str
        self.document_dir = document_dir
        self.filename = ''
        self.content = ''
        self.status = STATUS_OK
        self.date = datetime.now().strftime('Date: %a, %d %b %Y %H:%M:%S GMT +3').encode('utf-8')
        self.server = b'Server: python-server (Unix)'
        self.connection = b'Connection: close'

        self.create_response(path_str)

    def create_response(self, path_str):
        self.filename = self.document_dir + path_str
        if self.filename.endswith('/') and not ('.html' in path_str):
            self.filename += 'index.html'
            if not os.path.isfile(self.filename):
                self.status = STATUS_FORBIDDEN
                self.content = STATUS_FORBIDDEN
                return

        self.filename = unquote(self.filename)
        if '?' in self.filename:
            self.filename = self.filename.split('?')[0]

        if self.method != 'GET' and self.method != 'HEAD':
            self.status = STATUS_METHOD_NOT_ALLOWED
            return

        if not os.path.isfile(self.filename):
            self.status = STATUS_NOT_FOUND
            self.content = STATUS_NOT_FOUND
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
                self.content = STATUS_FORBIDDEN
                return

        self.status = STATUS_OK
        with open(self.filename, 'rb') as f:
            self.content = f.read()

    def to_str(self):
        response_bytes = b'HTTP/1.1 '
        response_bytes += self.status + EOL3
        response_bytes += self.date + EOL3
        response_bytes += self.server + EOL3
        response_bytes += self.connection + EOL3

        if self.status == STATUS_OK or self.status == STATUS_NOT_FOUND or self.status == STATUS_FORBIDDEN:
            response_bytes += self.get_content_type() + EOL3
            response_bytes += b'Content-Length: ' + bytearray(str(len(self.content)), encoding='utf-8') + EOL3
            response_bytes += EOL3  # Пустая строка
            if self.method != 'HEAD':
                response_bytes += bytearray(self.content) + b'\r\n'

        return response_bytes

    def get_content_type(self):
        content_type = b'Content-Type: '
        if self.filename.lower().endswith('.html') or self.status == STATUS_NOT_FOUND:
            content_type += b'text/html'
        elif self.filename.lower().endswith('.css'):
            content_type += b'text/css'
        elif self.filename.lower().endswith('.js'):
            content_type += b'application/javascript'
        elif self.filename.lower().endswith('.jpg') or self.filename.lower().endswith('.jpeg'):
            content_type += b'image/jpeg'
        elif self.filename.lower().endswith('.png'):
            content_type += b'image/png'
        elif self.filename.lower().endswith('.gif'):
            content_type += b'image/gif'
        elif self.filename.lower().endswith('.swf'):
            content_type += b'application/x-shockwave-flash'
        else:
            content_type += b'text/plain'

        return content_type
