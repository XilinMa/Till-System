#!/usr/bin/env python
"""
Very simple HTTP server in python.
Usage::
    ./dummy-web-server.py [<port>]
Send a GET request::
    curl http://localhost
Send a HEAD request::
    curl -I http://localhost
Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from response import server_response


class S(BaseHTTPRequestHandler):

    total_amount = 0

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        # path means message received from front-end(html, js) or current location
        parts = self.path.split("?", 1)

        if self.path == '/':
            self.send_response(200)
            fname = 'till.html'
            file = open(fname, "r")
            text = file.read()
            self.send_header('Content-type', 'text/html')
        elif self.path == '/till.css':
            fname = 'till.css'
            file = open(fname, "r")
            text = file.read()
            self.send_header('Content-type', 'text/css')
            self.send_response(200)
        elif self.path == '/till2.html':
            self.send_response(200)
            fname = 'till2.html'
            file = open(fname, "r")
            text = file.read()
            self.send_header('Content-type', 'text/html')
        elif self.path == '/till.js':
            self.send_response(200)
            fname = 'till.js'
            file = open(fname, "r")
            text = file.read()
            self.send_header('Content-type', 'application/javascript')
        elif parts[0] == '/action':
            self.send_response(200)

            # 1. process requests and get parameters from response
            params = parts[1].split('&')

            text = server_response(params)
            self.send_header('Content-type', 'application/xml')

        else:
            self.send_response(404)
            fname = '404.html'
            file = open(fname, "r")
            text = file.read()
            self.send_header('Content-type', 'text/html')

        self.end_headers()
        # response to client
        self.wfile.write(text.encode())

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")


def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)

    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
