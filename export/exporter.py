from google.appengine.ext import db
from google.appengine.tools import bulkloader
from google.appengine.ext import ndb

class Employee(db.Model):
    firstname = db.StringProperty()
    lastname = db.StringProperty()
    phone = db.StringProperty()
    residence = db.StringProperty()
    date = db.StringProperty()
    time = db.StringProperty()


def toUtf8( str ):
    if (str):
        return str.encode('utf-8')
    else:
        return None
    
class AlbumExporter(bulkloader.Exporter):
    def __init__(self):
        bulkloader.Exporter.__init__(self, 'Employee',
                                    [('firstname', toUtf8, ''),
                                     ('lastname', toUtf8, ''),
                                     ('residence', toUtf8, ''),
                                     ('date', toUtf8, ''),
                                     ('time', toUtf8, ''),
                                     ('phone', toUtf8, ''),
                                    ])


exporters = [AlbumExporter]