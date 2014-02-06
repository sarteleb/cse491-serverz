import random
import socket
import time
import urlparse
import cgi
import jinja2
from StringIO import StringIO

def main():
    s = socket.socket()         # Create a socket object
    host = socket.getfqdn() # Get local machine name
    port = random.randint(8000, 9999)
    s.bind((host, port))        # Bind to the port

    print 'Starting server on', host, port
    print 'The Web server URL for this would be http://%s:%d/' % (host, port)

    s.listen(5)                 # Now wait for client connection.

    print 'Entering infinite loop; hit CTRL-C to exit'
    
    while True:
        # Establish connection with client.    
        c, (client_host, client_port) = s.accept()
        handle_connection(c)
        

# Handles the connection
def handle_connection(conn):
    loader = jinja2.FileSystemLoader('./templates')
    env = jinja2.Environment(loader = loader)
    
    request = conn.recv(1)

    while request[-4:] != '\r\n\r\n':
        request += conn.recv(1)
    
    request_info = request.split('\r\n')[0].split(' ')

    request_type = request_info[0]

    try:
        url_parsed = urlparse.urlparse(request_info[1])
        url_path = url_parsed[2]
    except:
        handle_no_page(conn, '', env)
        return

    if request_type == 'POST':
        headers_dict, content = parse_post_request(conn, request)
        environ = {}
        environ['REQUEST_METHOD'] = 'POST'

        print request + content
        form = cgi.FieldStorage(headers = headers_dict, fp = StringIO(content), environ = environ)

        if url_path == '/':
            handle_index(conn, '', env)
        elif url_path == '/submit':
            handle_submit_post(conn, form, env)
        else:
            handle_no_page(conn, '', env)
    else:
        print request
        if url_path == '/':
            handle_index(conn, '', env)
        elif url_path == '/content':
            handle_content(conn, '', env)
        elif url_path == '/file':
            handle_file(conn, '',env)
        elif url_path == '/image':
            handle_image(conn, '', env)
        elif url_path == '/form':
            handle_form(conn, '', env)
        elif url_path == '/submit':
            handle_submit_get(conn,url_parsed[4], env)
        else:
            handle_no_page(conn, '', env)
    conn.close()


def handle_index(conn, parameters, env):
    toSend = 'HTTP/1.0 200 OK\r\n' + \
             'Content-type: text/html\r\n\r\n' + \
             env.get_template("index.html").render()
             
    conn.send(toSend)

def handle_content(conn, parameters, env):
    toSend = 'HTTP/1.0 200 OK\r\n' + \
             'Content-type: text/html\r\n\r\n' + \
             env.get_template("content.html").render()
    conn.send(toSend)

def handle_file(conn, parameters, env):
    toSend = 'HTTP/1.0 200 OK\r\n' + \
             'Content-type: text/html\r\n\r\n' + \
             env.get_template("file.html").render()
    conn.send(toSend)

def handle_image(conn, parameters, env):
    toSend = 'HTTP/1.0 200 OK\r\n' + \
             'Content-type: text/html\r\n\r\n' + \
             env.get_template("image.html").render()
    conn.send(toSend)

def handle_form(conn, parameters, env):
    forms = 'HTTP/1.0 200 OK\r\n' + \
            'Content-type: text/html\r\n' + \
            '\r\n' + \
            env.get_template("form.html").render()

    conn.send(forms)

def handle_submit_post(conn, form, env):
    try:
      firstname = form['firstname'].value
    except KeyError:
      firstname = ''
    try:
      lastname = form['lastname'].value
    except KeyError:
      lastname = ''
    vars = dict(firstname = firstname, lastname = lastname)
    template = env.get_template("submit_result.html")
    
    response = 'HTTP/1.0 200 OK\r\n' + \
            'Content-type: text/html\r\n' + \
            '\r\n' + \
            env.get_template("submit_result.html").render(vars)
            
    conn.send(response)        
def handle_submit_get(conn, params, env):
    params = urlparse.parse_qs(params)

    try:
      firstname = params['firstname'][0]
    except KeyError:
      firstname = ''
    try:
      lastname = params['lastname'][0]
    except KeyError:
      lastname = ''

    vars = dict(firstname = firstname, lastname = lastname)
    template = env.get_template("submit_result.html")
    
    response = 'HTTP/1.0 200 OK\r\n' + \
            'Content-type: text/html\r\n' + \
            '\r\n' + \
            env.get_template("submit_result.html").render(vars)
            
    conn.send(response)

def handle_no_page(conn, parameters, env):
    toSend = 'HTTP/1.0 404 Not Found\r\n' + \
             'Content-type: text/html\r\n\r\n' + \
             env.get_template("404.html").render()
    conn.send(toSend)

def handle_post(conn, info):
    toSend = 'HTTP/1.0 200 OK\r\n' + \
             'Content-type: text/html\r\n\r\n' + \
             '<h2>hello world</h2>'
    conn.send(toSend)

def parse_post_request(conn, request):
  header_dict = dict()

  request_split = request.split('\r\n')

  for i in range(1,len(request_split) - 2):
    header = request_split[i].split(': ', 1)
    header_dict[header[0].lower()] = header[1]

  content_length = int(header_dict['content-length'])
  
  content = ''
  for i in range(0,content_length):
    content += conn.recv(1)

  return header_dict, content


if __name__ == '__main__':
    main()
