#!/usr/bin/env python
import sys
import random
import socket
import urlparse
import StringIO
import quixote
import imageapp

from app import make_app
# from quixote.demo import create_publisher
# from quixote.demo.mini_demo import create_publisher
# from quixote.demo.altdemo import create_publisher
# from wsgiref.validate import validator

def main():
    s = socket.socket() # Create a socket object.
    host = socket.getfqdn() # Get local machine name.
    port = random.randint(8000, 9999) # Assign random port.
    s.bind((host, port)) # Bind to the port.

    # imageapp.setup()
    wsgi_app = make_app() # Creates WSGI app.
    # validate_app = validator(wsgi_app)
    # p = create_publisher()
    # p = imageapp.create_publisher()
    # wsgi_app = quixote.get_wsgi_app()

    print 'Starting server on', host, port
    print 'The Web server URL for this would be http://%s:%d/' % (host, port)

    s.listen(5) # Now wait for client connection.

    print 'Entering infinite loop; hit CTRL-C to exit'
    while True:
        # Establish connection with client.
        c, (client_host, client_port) = s.accept()
        print 'Got connection from', client_host, client_port
        handle_connection(c, wsgi_app)
        # handle_connection(c, validate_app)
    return

def handle_connection(conn, wsgi_app):
    # Read in request until end of header sentinel.
    request = ''
    while '\r\n\r\n' not in request:
        request += conn.recv(1)

    # Avoids indexing error - makes sure there is request.
    if not request:
        conn.close()
        return

    # Creates headers dictionary.
    headers = {}
    for header in request.splitlines()[1:]:
        try:
            k, v = header.split(': ', 1)
        except:
            continue
        headers[k.lower()] = v

    # Read in rest of request to obtain message.
    message = ''
    if 'content-length' in headers:
        while len(message) < int(headers['content-length']):
            message += conn.recv(1)

    # Creates environ dictionary.
    environ = {}
    environ['REQUEST_METHOD'] = request.splitlines()[0].split(' ')[0]
    url = urlparse.urlparse(request.splitlines()[0].split(' ')[1])
    environ['PATH_INFO'] = url.path
    environ['QUERY_STRING'] = url.query
    environ['CONTENT_TYPE'] = headers.get('content-type', '')
    environ['CONTENT_LENGTH'] = headers.get('content-length', '')
    environ['wsgi.input'] = StringIO.StringIO(message)
    # Used by Quixote apps.
    environ['SCRIPT_NAME'] = ''
    # Used to pass WSGI Validation.
    environ['SERVER_NAME'] = 'My Server'
    environ['SERVER_PORT'] = 'My Port'
    environ['wsgi.version'] = (1, 0)
    environ['wsgi.errors'] = sys.stderr
    environ['wsgi.multithread'] = False
    environ['wsgi.multiprocess'] = False
    environ['wsgi.run_once'] = False
    environ['wsgi.url_scheme'] = 'http'
    # Used to handle cookies.
    environ['HTTP_COOKIE'] = headers.get('cookie', '')

    # Declares variables in dictionary so they can be changed by start_response.
    # Python 2.x doesn't support nonlocal keyword.
    local = {'response' : '', 'started' : False}

    # Defines start_response function.
    def start_response(status, response_headers):
        local['started'] = True

        # Restarts response every time function is called.
        local['response'] = ''

        # Appends status line and headers.
        local['response'] += 'HTTP/1.0 {0}\r\n'.format(status)
        for header in response_headers:
            local['response'] += '{0}: {1}\r\n'.format(header[0], header[1])
        local['response'] += '\r\n' # Ends with header sentinel.

        return

    # Gets content of response from call to WSGI app.
    for response in wsgi_app(environ, start_response):
        local['response'] += response

    # Send response.
    # (As long as start_response called)
    if local['started']:
        conn.send(local['response'])
    conn.close()
    return


if __name__ == '__main__':
    main()
