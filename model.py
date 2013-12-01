from google.appengine.ext import ndb

def exist(key):
    return key.get()

class Employee(ndb.Model):
    firstname = ndb.StringProperty(default = '')
    lastname = ndb.StringProperty(default = '')
    residence = ndb.StringProperty(default = '')
    phone = ndb.StringProperty(default = '')
    date = ndb.StringProperty(default = '')
    time = ndb.StringProperty(default = '')
    lastUpdate = ndb.DateTimeProperty('Last changed (UTC)', auto_now = True)
    # timestamp TODO
