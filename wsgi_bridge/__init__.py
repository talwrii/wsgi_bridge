import webob
import io
import http.server
import email.message

class WsgiServer(object):
    def __init__(self, handler):
        class patched_handler(WsgiHttpRequestHandler, handler):
            pass
        self.patched_handler = patched_handler

    def serve(self, environ, start_response):
        handler = self.patched_handler()
        handler.load_wsgi(environ, start_response)
        handler.handle_one_request()
        return [handler.wfile.getvalue()]


class ByteAndStringIO(object):
    "Like ByteIO but encode strings to utf8 if strings are given"

    def __init__(self):
        self.wrapped = io.BytesIO()

    def write(self, value):
        if isinstance(value, str):
            # This might return the wrong value
            return self.wrapped.write(str.encode('utf8'))
        elif isinstance(value, bytes):
            return self.wrapped.write(value)
        else:
            raise ValueError(value)

    def getvalue(self):
        return self.wrapped.getvalue()


class WsgiHttpRequestHandler(http.server.BaseHTTPRequestHandler):
    """Mixin class to replace BaseHttpRequestHandler functionality with code that uses
    a wsgi interface instead.

    Data is cached before being sent which may affect latency. But is necessary
    due to interface mismatches (unless multithreading is used - which is undesireable).

    This class works by replacing methods and objects on an HttpRequestHandler object with methods
    that collect data that is then used after handle_one_request has finished to
    return a response. This means data that might have been streamed is cached.

    """
    def __init__(self):
        self.wfile = ByteAndStringIO()

    def load_wsgi(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response
        self.code  = None
        self.response_headers = []

    def handle_one_request(self):
        request = webob.Request(self.environ)
        self.path = request.path
        self.command = request.method
        self.version = self.environ['SERVER_PROTOCOL']

        reconstructed_envelope = SeekableBytesIO('\r\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()).encode('utf8'))
        print(reconstructed_envelope.readline())
        self.headers = http.client.parse_headers(reconstructed_envelope, self.MessageClass)

        method_name = 'do_' + request.method
        if not hasattr(self, method_name):
            raise NotImplementedError()
        getattr(self, method_name)()

    def send_response(self, code, message=None):
        self.code = code
        self.message = message

    def send_header(self, key, value):
        self.response_headers.append((key, value))

        if key.lower() == 'connection':
            if value.lower() == 'close':
                self.close_connection = 1
            elif value.lower() == 'keep-alive':
                self.close_connection = 0

    def end_headers(self):
        status = '{}'.format(self.code.value)
        message = self.message or self.code.phrase
        status += ' ' + message
        self.start_response(status, self.response_headers)

class SeekableBytesIO(object):
    "A wrapped stringIO that has the concept of a current location"
    def __init__(self, value):
        if not isinstance(value, bytes):
            raise TypeError(value)

        self.value = value
        self.index = 0

    def readline(self, maxlen=None):
        del maxlen # ignore max length argument
        if self.index == -1:
            return b''
        else:
            new_index = self.value.find(b'\n', self.index)
            if new_index == -1:
                result = self.value[self.index:]
                self.index = -1
            else:
                result = self.value[self.index:new_index] + b'\n'
                self.index = new_index + 1
            print("Returning ", repr(result))
            return result





if __name__ == '__main__':
    import wsgiref.simple_server
    server = wsgiref.simple_server.make_server('localhost', 8000, WsgiServer(http.server.SimpleHTTPRequestHandler).serve)
    server.serve_forever()
