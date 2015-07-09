import os
import sys
from os import path as op
here = op.realpath(op.dirname(__file__))
there = os.getcwd()
with_here = lambda *x: op.join(here,*x)
if op.exists(with_here('venv')):
    sys.path.insert(0,with_here('venv','lib','python2.7','site-packages'))
from commands import getoutput
from flask import Flask,request,make_response,render_template
import json

HTTP, HTTPS = 'http://','https://'

class WSGIBase(object):
    def __init__(self,app_path=None,app=None,index_file=None):
        self._index_file = index_file or 'index.php'
        self.app = app
        self.app_path = app_path and op.realpath(op.join(there,app_path))
        
    @property
    def index_file(self):
        return op.join(self.app_path,self._index_file)


class PhpWsgiAppMiddleware(WSGIBase):

    CMD = 'php -f {0}'

    def __init__(self,ctx,*args,**kwargs):
        self.app_ctx = ctx
        super(PhpWsgiAppMiddleware,self).__init__(*args,**kwargs)

    def _get_cmd(self):
        has_php = op.exists(self.index_file)
        return has_php and self.CMD.format(self.index_file)

    def _run_php(self,url):        
        self.app_ctx.push()

        os.environ['REQUEST_URI'] = url        
        os.environ['REQUEST_METHOD'] = request.method.upper()
        os.environ['PHP_SELF'] = self.index_file
        os.environ['SERVER_PROTOCOL'] = HTTP if not request.is_secure else HTTPS
        os.environ['HTTP_HOST'] = request.host
        self.app_ctx.pop()
        return self._get_cmd() and getoutput(self._get_cmd())

    def __call__(self,environ,start_response):
        self._run = True
        file_location = '{}{}'.format(self.app_path,environ.get('PATH_INFO'))        
        if op.exists(file_location) and op.isfile(file_location):
            self._run = False            
            if file_location.endswith('.php'):
                self._index_file = file_location
                self._run = True
        if self._run:
            res = self._run_php(environ.get('PATH_INFO'))
            if res:
                content_type = 'text/html'
                status = '200 OK'
                try:
                    json.loads(res)
                    content_type = 'application/json'
                except:
                    pass
                start_response(status,[('content-type',content_type),('User-Agent','Python-php-app')])
                return res
            else:
                status = '404 ERROR'
                error = 'script_file -> {} not found'.format(self.index_file)
                start_response(status,[])
                return error

        return self.app(environ,start_response)

class StaticWSGIWrapperMiddleware(WSGIBase):

    type_map = {
        'js':'javascript',
        'css':'css',
        'png':'image',
        'jpg':'image',
        'tiff':'image',
        'html':'html'
    }
    
    def __call__(self,environ,start_response):
        verbose = os.environ.get('VERBOSE') 
        file_location = '{}{}'.format(self.app_path,environ.get('PATH_INFO'))  
        if op.splitext(file_location)[-1] != '':
            if op.exists(file_location) and op.isfile(file_location):
                if file_location.endswith('.php'):
                    return self.app(environ,start_response)
                content_type = 'text/{}'.format(self._get_content_type(file_location))                
                if verbose:
                    print 'SERVING STATIC FILE {0}'.format(file_location)
                start_response('200',[('content-type',content_type),('User-Agent','Python-php-static')])
                return open(file_location,'r').read()
            else:
                status = '404 ERROR'
                error = 'script_file -> {} not found'.format(file_location)
                start_response(status,[])
                return error
        return self.app(environ,start_response)

    def _get_content_type(self,filename):
        return self.type_map.get(filename.rsplit('.',1)[-1])
        

class PhpWsgiApp(object):
    # example of using to run php app
    # first get a python wsgi app to wrap our 
    # middlewares with
    def __init__(self,app_path=None,app=None,):
        self.app_path = app_path or there
        if app is None:
            app = Flask(__name__)
        self.app = app
        ctx = app.test_request_context()
        # and add our php handler
        self.app.wsgi_app = PhpWsgiAppMiddleware(ctx,self.app_path,self.app.wsgi_app)
        # now add our static handler
        self.app.wsgi_app = StaticWSGIWrapperMiddleware(self.app_path,self.app.wsgi_app)

    def __call__(self,environ,start_response):
        return self.app(environ,start_response)

    def run(self,*args,**kwargs):
        self.app.run(*args,**kwargs)

if __name__ == "__main__":
    app = PhpWsgiApp()
    app.run(host='0.0.0.0',port=9900,debug=True)
