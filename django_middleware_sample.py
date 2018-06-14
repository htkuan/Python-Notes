class BaseMiddleware:
    def __init__(self, do_something):
        self.do_something = do_something
        super().__init__()
    
    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
            print(f'BaseMiddleware process_request {response}')
        if not response:
            response = self.do_something(request)   
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
            print(f'BaseMiddleware process_response {response}')
        return response

class MiddlewareOne(BaseMiddleware):
    def process_request(self, request):
        print('Middleware 1 in')
        
    def process_response(self, request, response):
        print('Middleware 1 out')
        return response
    
class MiddlewareTwo(BaseMiddleware):
    def process_request(self, request):
        print('Middleware 2 in')
    
    def process_response(self, request, response):
        print('Middleware 2 out')
        return response
    
class Handler:
    def __init__(self):
        super().__init__()
        self.load_middleware()
    
    def __call__(self, wgsi_request):
        response = self.middleware_chain(wgsi_request)
        return response
    
    def load_middleware(self):
        handler = wrap(do_something)
        for middleware in [MiddlewareTwo, MiddlewareOne]:
            mw_instance = middleware(handler)
            handler = wrap(mw_instance)
            
        self.middleware_chain = handler

def wrap(do_something):
    
    def inner(request):
        print(f'warp in {request}')
        response = do_something(request)
        print(f'warp out {response}')
        return response
    
    return inner

def do_something(request):
    print('do_something')
    response = f'this is response {request}'
    return response

if __name__ == '__main__':
    middleware = Handler()
    middleware('xxx')
