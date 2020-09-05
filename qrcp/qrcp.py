import socket
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from os import chdir, path
from socketserver import ThreadingMixIn
from shutil import copyfile
from tempfile import TemporaryDirectory

import pyqrcode


START_PORT = 8000


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class NoCacheHTTPRequestHandler(SimpleHTTPRequestHandler):
    def send_response_only(self, code, message=None):
        super().send_response_only(code, message)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Expires', '0')


def get_local_ip():
    '''
    returns routable ip if we have one.
    Otherwise, we'll hope gethostbyname() can come up clutch.
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        return socket.gethostbyname(socket.gethostname())
    finally:
        s.close()
    return ip


def bind_server():
    port = START_PORT
    for i in range(0, 50):  # if you have all 50 of these ports in use, I don't know what to say
        try:
            return ThreadedHTTPServer(("", port+i), NoCacheHTTPRequestHandler)
        except OSError:
            pass


def render_qr(url):
    eqr = pyqrcode.create(url)
    print(eqr.terminal())


def main():
    if len(sys.argv) < 2:
        print('usage: qrcp <filename>')
        exit(1)

    filename = sys.argv[1]
    basename = path.basename(filename)

    with TemporaryDirectory() as tempdir:
        copyfile(filename, '{}/{}'.format(tempdir, basename))
        chdir(tempdir)

        http = bind_server()
        url = '{}:{}/{}'.format(get_local_ip(), http.server_address[1], basename)
        print('Running server on {}'.format(url))

        render_qr(url)
        with http as httpd:
            httpd.serve_forever()


if __name__ == '__main__':
    main()
