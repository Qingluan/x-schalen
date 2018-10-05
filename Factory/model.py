from qlib.data import dbobj
# this is just template , will be parse to 
# written by Qingluan 
# CREATE TABLE task (
#        ID INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT ,
#        CreatedTime TimeStamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
#        task_name varchar(255) not null default "default_task",
#        status varchar(255) not null default "status",
#        url TEXT)
#
#
#

class Msg(dbobj):pass
    # sender
    # reciver 
    # group  
    # content 
    # send_time
class Key(dbobj):pass
class Token(dbobj):pass
    