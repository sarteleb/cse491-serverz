# from http://docs.python.org/2/library/wsgiref.html
import cgi
import urlparse
import jinja2
from wsgiref.util import setup_testing_defaults

# A relatively simple WSGI application. It's going to print out the
# environment dictionary after being updated by setup_testing_defaults
def simple_app(environ, start_response):
    loader = jinja2.FileSystemLoader('./templates')
    env = jinja2.Environment(loader = loader)
    print(environ)

    status = '404 Not Found'
    ret = handle_no_page('', env)
    headers = [('Content-type', 'text/html')]

    try:
        info = environ['REQUEST_METHOD']
        url_path = environ['PATH_INFO']
    except:
        pass

    if info == 'POST':
        if url_path == '/':
            status = '200 OK'
            ret = handle_index(environ, env)
        elif url_path == '/submit':
            status = '200 OK'
            ret = handle_submit_post(environ, env)
    elif info == 'GET':
        if url_path == '/':
            status = '200 OK'
            ret = handle_index(environ, env)
        elif url_path == '/content':
            status = '200 OK'
            ret = handle_content(environ, env)
        elif url_path == '/file':
            headers = [('Content-type', 'text/plain')]
            status = '200 OK'
            ret = handle_file(environ, env)
        elif url_path == '/image':
            headers = [('Content-type', 'image/jpeg')]
            status = '200 OK'
            ret = handle_image(environ, env)
        elif url_path == '/form':
            status = '200 OK'
            ret = handle_form(environ, env)
        elif url_path == '/submit':
            status = '200 OK'
            ret = handle_submit_get(environ, env)
                
    start_response(status, headers)
    return ret 

def handle_index(parameters, env):
   return str(env.get_template("index.html").render())
             

def handle_content(parameters, env):
    return str(env.get_template("content.html").render())

def handle_file(parameters, env):
    return read_file('./files/something.txt')         

def handle_image(parameters, env):
    return read_file('./images/something.jpeg')        

def handle_form(parameters, env):
    return str(env.get_template("form.html").render())

def handle_submit_post(environ, env):
    headers = {}
    for i in environ.keys():
        headers[i.lower()] = environ[i]
    form = cgi.FieldStorage(headers = headers, fp = environ['wsgi.input'], environ = environ)
    try:
      firstname = form['firstname'].value
    except KeyError:
      firstname = ''
    try:
      lastname = form['lastname'].value
    except KeyError:
      lastname = ''
    vars = dict(firstname = firstname, lastname = lastname)
    return str(env.get_template("submit_result.html").render(vars))
            
def handle_submit_get(environ, env):
    parameters = environ['QUERY_STRING']
    parameters = urlparse.parse_qs(parameters)

    try:
      firstname = parameters['firstname'][0]
    except KeyError:
      firstname = ''
    try:
      lastname = parameters['lastname'][0]
    except KeyError:
      lastname = ''

    vars = dict(firstname = firstname, lastname = lastname)
    return str(env.get_template("submit_result.html").render(vars))


def handle_no_page(parameters, env):
    return str(env.get_template("404.html").render())

def read_file(file_name):
    fp = open(file_name, 'rb')
    read_in = fp.read()
    fp.close()
    return read_in

def make_app():
    return simple_app
