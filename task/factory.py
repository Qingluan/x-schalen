from mroylib.config import Config, ConfigParser
from qlib.data import dbobj, Cache

from hashlib import md5
import time
import os
import random
from task.manager import Leader

J = os.path.join
E = os.path.exists
mk = os.mkdir
ls = os.listdir
ep = os.path.expanduser 

conf = Config(name="x-schalen.ini")
HOST_DB = conf['host-db']
class Host(dbobj):pass
class Book(dbobj):
    def get_servers(self):
        return self.workers.split('|')

    def get_factory(self):
        return Factory.load(self.name)

class Builder:

    def build_from_planet(self, conf_str):
        con = ConfigParser()
        con.read_string(conf_str)
        f = Factory()
        num = con.get('info', 'num')
        f.new(num)
        with open(J(conf['session-db-dir'], f._name +".conf") ,'w') as fp:
            fp.write(conf_str)
        f.build()



class Factory:

    def __init__(self, name=None):
        self._workers = []
        self._name = "Uninit"
        self._session_db = "Uninit"
        self._conf = None
        if name:
            self._load(name)

    @classmethod
    def load(cls, name):
        c = cls()
        c._load(name)
        return c

    @classmethod
    def list(cls):
        c = Cache(conf['session-db'])
        return list(c.query(Book))

    def _load(self, name):
        c = Cache(conf['session-db'])
        index = c.query_one(Book, name=name)
        if index:
            self._workers = index.get_servers()
            self._name = name
            self._session_db = Cache(os.path.join(conf['session-db-dir'], name +".db"))
            self._conf = Config(file=J(conf['session-db-dir'], name +".conf"))
            return self._name
        return 'Not found'


    def new(self, num=8):
        self._workers = [h for h in self._dispatch_servers(num)]
        self._name = str(int(time.time()))
        self._session_db = Cache(os.path.join(conf['session-db-dir'], self._name +".db"))
        index = Book(name=self._name, workers='|'.join(self._workers))
        # pdb.set_trace()
        c = Cache(conf['session-db'])
        index.save(c)
        return self._name

    def build(self):
        os.mkdir(os.path.join(conf['session-db-dir']), self._name)
        if E(J(conf['session-db-dir'], self._name + ".conf")):
            return self._install()

    def _install(self):
        self._conf = Config(file=J(conf['session-db-dir'], self._name +".conf"))
        self._conf.section = 'dependence'
        res = {}
        for component in self._conf.keys:
            cmd = self._conf[component]
            res[component] = os.popen(cmd).read()
        return res

    def __repr__(self):
        return self._name

    def _dispatch_servers(self, num):
        _host_db = Cache(HOST_DB)
        hs =  [i.host for i in _host_db.query(Host)]
        c = 0
        while 1:
            w = random.randint(0, len(hs))
            yield hs.pop(w)
            c += 1
            if c >= num:
                break
            if len(hs) == 0:
                break


    def destroy(self):
        c = Cache(conf['session-db'])
        index = c.query_one(Book, name=self._name)
        c.delete(index)

    def report(self):
        pass


    def dispatch(self):
        l = Leader(self._conf)
        l.dispatch(self._workers)


