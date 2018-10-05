

## write by qingluan 
# this is a config file
# include db and debug , static path 
import os
from os import path
# here to load all controllers
# from Qtornado.log import LogControl
from .controller import *
import logging as L
from qlib.data import Cache, dbobj
# load ui modules
import Reserver.ui as ui
import sys
import os
from mroylib.config import Config
# db engine 
# db_engine = pymongo.Connection()['local']
config = Config(name='x-schalen.ini')
db_connect_cmd = os.path.expanduser(config['server-db'])
print("-- connecto db:", db_connect_cmd)
db_engine = Cache(db_connect_cmd)


# static path 
rdir_path = os.path.dirname(__file__)
static_path = os.path.join(rdir_path ,"static")
files_path = os.path.join(static_path ,"files")

# set log level
# LogControl.LOG_LEVEL |= LogControl.OK
# LogControl.LOG_LEVEL |= LogControl.INFO

Settings = {
        'db':db_engine,
        'L': L,
        'debug':True,
        "ui_modules": ui,
        'autoreload':True,
        'cookie_secret':'This string can be any thing you want',
        'static_path' : static_path,
    }


## follow is router
try:
    os.mkdir(files_path)
except FileExistsError:
    pass
#
appication = tornado.web.Application([
                (r'/', IndexHandler),
                # add some new route to router
                ##<route></route>
                # (r'/main',MainHandler),
         ],**Settings)


# setting port 
port = 8080

