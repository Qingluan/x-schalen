from hashlib import sha256
import zlib
import pickle
import time
from base64 import b64decode, b64encode
import logging
import requests
import json
import os
import re
from .model import Key
from mroylib.config import Config
import argparse
# import pdb

MSG_DB = "~/.qqbot-tmp/msg-db.sql"


def data_fact(data, en=False, if_zip=True):
    if isinstance(data, str):
        data = data.encode('utf-8')

    if en:
        if if_zip:
            data = zlib.compress(data)
        mac = sha256(data).hexdigest()
        return data, if_zip, mac
    else:
        mac = sha256(data).hexdigest()
        if if_zip:
            data = zlib.decompress(data)
        return data, if_zip, mac


def obj2data(objs, if_zip=True):
    data = pickle.dumps(objs)
    en_data, if_zip, mac = data_fact(data, en=True, if_zip=if_zip)
    return en_data, if_zip, mac


def data2obj(data, if_zip=True):
    data, if_zip, mac = data_fact(data, if_zip=if_zip)
    return pickle.loads(data), if_zip, mac


def package(obj, if_zip=True):
    bdata, if_zip, mac = obj2data(obj, if_zip)
    bdata = b64encode(bdata).decode('utf-8')
    return {
        'data': bdata,
        'if_zip': if_zip,
        'mac': mac
    }


def unpackage(obj, if_zip=True):
    data = obj['data'].encode('utf-8')
    if_zip = obj['if_zip']
    mac = obj['mac']
    data = b64decode(data)
    objs, if_zip, lmac = data2obj(data, if_zip)
    if mac != lmac:
        logging.warn("Msg is check failed!")
    return objs


class MsgMan:
    d = []
    init_time = None

    def __init__(self, ti=5, api='http://localhost:14144/'):
        self._time = ti
        if not MsgMan.init_time:
            MsgMan.init_time = time.time()

        self.api = api

    def save(self, msg):
        MsgMan.d.append(msg)

    def test(self):
        res = requests.get("http://localhost:14144/")
        if res.status_code == 200:
            return True
        return False

    def clear(self):
        MsgMan.d = []
        MsgMan.init_time = time.time()

    def syncs_msg(self, msg):
        n = time.time()
        l = MsgMan.init_time
        api = self.api
        q = self._time
        self.save(msg)
        if n - l > q:
            msgs = MsgMan.d
            data = package(msgs)
            # print("test ... res = requests.post(api, data=data).json()")
            print(data)
            res = requests.post(api, data=data).text
            print(res)
            self.clear()
        else:
            print('collect:', len(MsgMan.d))


def config_json(json_file, key, val):
    if not os.path.exists(json_file):
        print("no json file found: %s" % json_file)
        return
    d = None
    old = None
    try:
        with open(json_file) as fp:
            d = json.load(fp)
            old = d.copy()
            d[key] = val
        dd = json.dumps(d)
    except Exception:
        print("not json file: %s" % json_file)
        return

    try:
        with open(json_file, 'w') as fp:
            json.dump(d, fp)
            print(key, '->', val)
    except Exception:
        with open(json_file, 'w') as fp:
            json.dump(old, fp)
        print("change failed . use old verion ")


def config_ini(ini_file, key, val, section='DEFAULT'):
    
    conf = Config(file=ini_file)
    if section not in conf.sections:
        section = conf.section

    conf.conf[section][key] = val
    try:
        with open(ini_file, 'w') as con:
            conf.conf.write(con)
    except Exception:
        with open(ini_file, 'w') as con:
            conf.conf.write(con)

    print(key, "->", val)


def set_conf(f, key, val, section='DEFAULT'):
    if not os.path.exists(f):
        print("no json file found: %s" % f)
        return
    if f.endswith(".ini") or f.endswith(".conf"):
        config_ini(f, key, val, section)
    elif f.endswith(".json"):
        config_json(f, key, val)
    else:
        print("not support file: %s"% f)


def list_conf(f=None):
    if f and os.path.exists(f) and os.path.isfile(f):
        with open(f) as fp:
            print(fp.read())
    else:
        for root, ds, fs in os.walk(os.path.expanduser("~/.config")):
            for f in fs:
                ff = os.path.join(root, f)
                if os.path.isfile(ff) and (ff.endswith(".json") or ff.endswith(".conf") or ff.endswith(".ini")):
                    print(ff)


def conf_cmd():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="*", help="file path")
    parser.add_argument("-l", "--list",action='store_true', default=False, help="list all conf file")
    
    parser.add_argument("-c", "--set", nargs="*", help=" key = val  key2 =val2 ")

    args = parser.parse_args()

    if args.list:
        list_conf()
    
    cmds = ''
    if args.set  and len(args.file) > 0:
        f = args.file[0]
        try:
            key, val =  ''.join(args.set).split("=",1)
            # if re.match(r'^\d*$', val.strip()):
            #     val = int(val)
            # else:
            #     val = val.strip()
            sec = 'DEFAULT'
            if key.count("::") == 1:
                sec,key = key.split("::")
            set_conf(f, key.strip(), val.strip(), section=sec)
        except Exception as e:
            print("error args : %s : %s" % (''.join(args.set), str(e)))
            return
    elif len(args.file) >0:
        for f in args.file:
            list_conf(f)

    

    
        

