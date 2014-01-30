import server

class FakeConnection(object):
    """
    A fake connection class that mimics a real TCP socket for the purpose
    of testing socket I/O.
    """
    def __init__(self, to_recv):
        self.to_recv = to_recv
        self.sent = ""
        self.is_closed = False

    def recv(self, n):
        if n > len(self.to_recv):
            r = self.to_recv
            self.to_recv = ""
            return r
            
        r, self.to_recv = self.to_recv[:n], self.to_recv[n:]
        return r

    def send(self, s):
        self.sent += s

    def close(self):
        self.is_closed = True

# Test a basic GET call.

def test_handle_index():
    conn = FakeConnection("GET / HTTP/1.0\r\n\r\n")

    expected_return = 'HTTP/1.0 200 OK\r\n' + \
             'Content-type: text/html\r\n\r\n' + \
             '<h1>Hello, world.</h1>' + \
             'This is sarteleb\'s web server.' + \
             '<ul>' + \
             '<li><a href="/content">Content</a></li>' + \
             '<li><a href="/file">Files</a></li>' + \
             '<li><a href="/image">Images</a></li>' + \
             '<li><a href="/form">Form</a></li>' + \
             '</ul>'
    
    server.handle_connection(conn)
    
    assert conn.sent == expected_return, 'Got: %s' % (repr(conn.sent),)

def test_handle_content():
    content_conn = FakeConnection("GET /content HTTP/1.0\r\n\r\n")

    content_return = 'HTTP/1.0 200 OK\r\n' + \
             'Content-type: text/html\r\n\r\n' + \
             '<h1>Welcome to sarteleb\'s content page!</h1>'

    server.handle_connection(content_conn)

    assert content_conn.sent == content_return, 'Got: %s' % (repr(content_conn.sent),)

def test_handle_file():
    file_conn = FakeConnection("GET /file HTTP/1.0\r\n\r\n")

    file_return = 'HTTP/1.0 200 OK\r\n' + \
             'Content-type: text/html\r\n\r\n' + \
             '<h1>Welcome to sarteleb\'s file page!</h1>'

    server.handle_connection(file_conn)

    assert file_conn.sent == file_return, 'Got: %s' % (repr(file_conn.sent),)

def test_handle_image():
    image_conn = FakeConnection("GET /image HTTP/1.0\r\n\r\n")
    
    image_return = 'HTTP/1.0 200 OK\r\n' + \
             'Content-type: text/html\r\n\r\n' + \
             '<h1>Welcome to sarteleb\'s image page!</h1>'
 
    
    server.handle_connection(image_conn)

    assert image_conn.sent == image_return, 'Got: %s' % (repr(image_conn.sent),)

def test_handle_form():
    form_conn = FakeConnection("GET /form HTTP/1.0\r\n\r\n")

    form_return = 'HTTP/1.0 200 OK\r\n' + \
            'Content-type: text/html\r\n' + \
            '\r\n' + \
            "<form action='/submit' method='GET'>" + \
            "First Name:<input type='text' name='firstName'>" + \
            "Last Name:<input type='text' name='lastName'>" + \
            "<input type='submit' value='Submit Get'>" + \
            "</form>\r\n" + \
            "<form action='/submit' method='POST'>" + \
            "First Name:<input type='text' name='firstName'>" + \
            "Last Name:<input type='text' name='lastName'>" + \
            "<input type='submit' value='Submit Post'>" + \
            "</form>\r\n"

    server.handle_connection(form_conn)

    assert form_conn.sent == form_return, 'Got: %s' % (repr(form_conn.sent),)
    

def test_post_request():
    post_conn = FakeConnection("POST /image HTTP/1.0\r\n\r\n")

    post_return = 'HTTP/1.0 200 OK\r\n' + \
             'Content-type: text/html\r\n\r\n' + \
             '<h2>hello world</h2>'

    server.handle_connection(post_conn)

    assert post_conn.sent == post_return, 'Got: %s' % (repr(post_conn.sent),)

def test_handle_get_submit():
    submit_conn = FakeConnection("GET /submit?firstName=Brandon&lastName=Sartele HTTP/1.0\r\n\r\n")

    submit_return = 'HTTP/1.0 200 OK\r\n' + \
             'Content-type: text/html\r\n\r\n' + \
             '<p>' + \
             'Hello Mr. Brandon Sartele.' + \
             '</p>'

    server.handle_connection(submit_conn)

    assert submit_conn.sent == submit_return, 'Got: %s' % (repr(submit_conn.sent),)

def test_handle_post_submit():
    submit_conn = FakeConnection("POST /submit HTTP/1.0\r\n\r\nfirstName=Brandon&lastName=Sartele")

    submit_return = 'HTTP/1.0 200 OK\r\n' + \
             'Content-type: text/html\r\n\r\n' + \
             '<p>' + \
             'Hello Mr. Brandon Sartele.' + \
             '</p>'

    server.handle_connection(submit_conn)

    assert submit_conn.sent == submit_return, 'Got: %s' % (repr(submit_conn.sent),)



