
import sys
try:
    # Setuptools entry point is slow.
    # If we have `festentrypoint` then use a fast entry point
    import fastentrypoints
except ImportError:
    sys.stdout.write('Not using fastentrypoints\n')
    pass


import setuptools
import os

HERE = os.path.dirname(__file__)

setuptools.setup(
    name='wsgi_bridge',
    version="0.1.0",
    author='Tal Wrii',
    author_email='talwrii@gmail.com',
    description='',
    license='MIT',
    keywords='',
    url='',
    packages=['wsgi_bridge'],
    long_description='',
    install_requires=['webob']
)
