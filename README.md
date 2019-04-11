# Wsgi bridge

This is a bridge between Python 3 standard library 

# Usage

`wsgi_bridge.WsgiServer` takes a [http.server]([http.server](https://docs.python.org/3/library/http.server.html)-based application and produces a wsgi application (as the object's `serve` method). This can then be called from a [wsgi server](https://wsgi.readthedocs.io/en/latest/servers.html) (in the code below we use the reference implementation of wsgi).

```
    import wsgiref.simple_server
    import wsgi_bridge
    server = wsgiref.simple_server.make_server('localhost', 8000, wsgi_bridge.WsgiServer(http.server.SimpleHTTPRequestHandler).serve)
    server.serve_forever()
```

# Motivation

This library was originally written by the author to use SimpleHttpServer
together with another wsgi component when writing code intended to be run
on a users system.

More generally wsgi is the defacto standard for python web applications,
with [many tools](https://wsgi.readthedocs.io/en/latest/libraries.html) for enhancing
and combining wsgi applications. Converting a `http.server`-based application to
to wsgi allows the application to interact with these tools. Additionally, in many
ways an application configured purely in python in more tractable and certainly easier
to distribute.

# Alternatives and prior work

* Before considering this tool, readers might like to look for alternative tools in the official [list of libraries](https://wsgi.readthedocs.io/en/latest/libraries.html) to see if an alternative exists.
* Depending on your use case you might prefer to use reverse proxying. This is supported by most large webservers (e.g. [nginx](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/), [apache](
https://httpd.apache.org/docs/2.4/howto/reverse_proxy.html)).
* Many of the features provided by wsgi (routing, middleware, chaining of operations) can be implemented in a near identical manner using proxying. In addition, proxying is arguably more scalable and easier to inspect. Certain wsgi implementations might provide for easier (i.e. in-process) sharing of state.
* This [stackoverflow question](https://stackoverflow.com/questions/30336945/interfacing-basehttpserver-to-wsgi-in-python) addresses the topic providing no solution.
