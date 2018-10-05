
## this is write by qingluan 
# just a inti handler 
# and a tempalte offer to coder
import json
import tornado
import tornado.web
from tornado.websocket import WebSocketHandler
from .model import Msg, Key, Token
from .utils import data2obj,obj2data, unpackage
from qlib.data import Cache
from concurrent.futures import ThreadPoolExecutor
import os


background_task_pocket = ThreadPoolExecutor(20)
MSG_DB = "~/.qqbot-tmp/msg-db.sql"

def run_background(func, callback, *args,loop=None, **kwds):
    def _callback(result):
        tloop = loop
        if not loop:
            tloop = tornado.ioloop.IOLoop.instance()

        tloop.add_callback(lambda: callback(result.result()))
    future = background_task_pocket.submit(func, *args, **kwds)
    future.add_done_callback(_callback)

def no_callback(*args):
    pass

class BackDb:
    data = []

    @staticmethod
    def save(o):
        BackDb.data.append(o)

    @staticmethod
    def extract_all():
        w = []
        print(BackDb.data)
        if len(BackDb.data) == 0:
            return []
        for o in BackDb.data:
            w.append(o.get_dict())
        BackDb.data = []
        return w

def back_query(callback, key,loop=None):
    def _query(key):
        db = Cache(os.path.expanduser(MSG_DB))
        list(db.fuzzy_search(Msg, key, BackDb.save))
        res = BackDb.extract_all()
        if res:
            return json.dumps(res)
        else:
            return json.dumps({"fail":"no found"})

    # tt = background_task_pocket.submit(_query, key)
    # tt.add_done_callback(lambda x: callback(x.result()))
    run_background(_query, callback, key, loop=loop)


class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.db = self.settings['db']
        self.L = self.settings['L']
    def get_current_user(self):
        return (self.get_cookie('user'),self.get_cookie('passwd'))
    def get_current_secure_user(self):
        return (self.get_cookie('user'),self.get_secure_cookie('passwd'))
    def set_current_seccure_user_cookie(self,user,passwd):
        self.set_cookie('user',user)
        self.set_secure_cookie("passwd",passwd)

    def load_page(self, name):
        d = os.path.join(os.path.dirname(name), 'template')
        self.L.info("loading from : %s" % d)
        if not name.endswith('.html'):
            name += '.html'
        return os.path.join(d, name)

class SocketHandler(WebSocketHandler):
    """ Web socket """
    clients = set()
    con = dict()
         
    @staticmethod
    def send_to_all(msg):
        for con in SocketHandler.clients:
            con.write_message(json.dumps(msg))
         
    @staticmethod
    def send_to_one(msg, id):
        SocketHandler.con[id(self)].write_message(msg)

    def json_reply(self, msg):
        self.write_message(json.dumps(msg))

    def open(self):
        SocketHandler.clients.add(self)
        SocketHandler.con[id(self)] = self
         
    def on_close(self):
        SocketHandler.clients.remove(self)
         
    def on_message(self, msg):
        SocketHandler.send_to_all(msg)



class SearchHandler(BaseHandler):


    @tornado.web.asynchronous
    def get(self):
        # L is log function , which include ok , info , err , fail, wrn
        self.L.info('got')
        # return self.render(self.template, post_page="/")
        self.write("fuck")
        self.finish()

    @tornado.web.asynchronous
    def _finish(self, data):
        self.write(data)
        self.finish()

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow 
        tloop = tornado.ioloop.IOLoop.instance()
        key = self.get_argument("key")
        back_query(self._finish, key, loop=tloop)
        

class SettingHandler(BaseHandler):


    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow 
        tloop = tornado.ioloop.IOLoop.instance()
        json_data = self.get_argument("setting")
        data = json.loads(json_data)
        if 'key' in data:
            key_v = data['key']
            db = Cache(os.path.expanduser(MSG_DB))
            k = Key(text=key_v)
            k.save(db)
            self.write(json.dumps({
                'res':'add key: %s'% key_v
                }))

        elif 'token' in data:
            key_v = data['token']

            db = Cache(os.path.expanduser(MSG_DB))
            t = Token(text=key_v, tp='ding')
            t.save(db)
            self.write(json.dumps({
                'res':'add ding token:%s'% key_v
                }))
        else:
            self.write("noting happend")

        self.finish()
        # back_query(self._finish, key, loop=tloop)


class IndexHandler(BaseHandler):
    
    def prepare(self):
        super(IndexHandler, self).prepare()
        self.template = self.load_page('index')

    @tornado.web.asynchronous
    def get(self):
        # L is log function , which include ok , info , err , fail, wrn
        self.L.info('got')
        return self.render(self.template, post_page="/")
        self.write("fuck")
        self.finish()

    @tornado.web.asynchronous
    def post(self):
        # you should get some argument from follow 
        data = self.get_argument("data")
        if_zip = self.get_argument("if_zip")
        if if_zip == 'true':
            if_zip = True
        mac = self.get_argument("mac")
        msgs = unpackage({
                'data':data,
                'if_zip':if_zip,
                'mac':mac,
            })
        
        db = Cache(os.path.expanduser(MSG_DB))
        db.save_all(*msgs)
        # .....
        # for parse json post
        # post_args = json.loads(self.request.body.decode("utf8", "ignore"))['msg']
        
        # redirect or reply some content
        # self.redirect()  
        self.write(json.dumps({
                'ok':len(msgs)
            }))
        self.finish()
    