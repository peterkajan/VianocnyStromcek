import os
import re
import logging
import jinja2
import webapp2
from model import Employee
from util import BaseHandler, sessionConfig
from google.appengine.ext import ndb
import urllib


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
    


ERROR_NOT_ENTERED = u'nie je vyplnený perník %s'
ERROR_WRONG_PHONE = u'máš zle vyplnený perník s tel. číslom. Povolené znaky sú: +, -, 0-9, /, \, medzera'

labels = {
         'residence' : u'adresa',
         'phone' : u'telefónne číslo',
         'date' : u'dátum doručenia',
         'time' : u'čas doručenia', 
}

def getUnenteredMsg( value ):
    return ERROR_NOT_ENTERED % (labels[ value ],)


def createTestEmployee():
    empl = Employee()
    empl.firstname = 'jozko'
    empl.lastname = 'mrkvicka'
    empl.sex ='m'
    empl.put()
    
class MainPage(BaseHandler):

    def displayPage(self, params, edit=False, errors=[], errorIds=[]):
        template_values = {
            'p': params,
            'errors': errors,
            'errorIds': errorIds,
            'edit' : edit,
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
        
    def get(self):
        #uncomment this to create test client in local repository on get request
        #createTestEmployee()
        keyUrl = self.request.get('key')
        logging.info('POST DB Key: ' + keyUrl)
        if not keyUrl:
            self.abort(404)
            
        key = ndb.Key( urlsafe = keyUrl )
        empl = key.get()
        if not empl:
            self.abort(404)
        
        logging.info('GET employee: ' + unicode(empl.firstname) + ' ' + unicode(empl.lastname))
        self.session['key'] = key.urlsafe()
        params = {}
        params['firstname'] = empl.firstname
        params['lastname'] = empl.lastname
        params['sex'] = empl.sex
            
        self.displayPage( empl, empl.residence )        
        
       
    def validatePhone(self, phone, errors, errorIds):
        if not phone:
            errors.append(getUnenteredMsg('phone'))
            errorIds.append('phone')
            return
            
        if not re.match(r'^[\+\\\-/0-9 ]+$', phone):    
            errors.append(ERROR_WRONG_PHONE)
            errorIds.append('phone')
        
    def validateData(self):
        errors = []
        errorIds = []
        
        if not self.request.get('residence'):
            errors.append( getUnenteredMsg( 'residence' ))
            errorIds.append('residence')
             
        self.validatePhone( self.request.get('phone'), errors, errorIds)
             
        if not self.request.get('date'):
            errors.append( getUnenteredMsg( 'date' ))
            errorIds.append('date')
            
        if not self.request.get('time'):
            errors.append( getUnenteredMsg( 'time' ))
            errorIds.append('time')
            
        return (errors, errorIds)
            
            
    def post(self):
        logging.info('POST DB Key: ' + self.session.get('key'))
        errors, errorIds = self.validateData() 
        key = ndb.Key( urlsafe = self.session.get('key'))
        empl = key.get()
        
        if errors:
            self.displayPage( self.request.params, empl.residence, errors, errorIds )
            return        
        
        logging.info('Successfull POST employee: ' + unicode(empl.firstname) + ' ' + unicode(empl.lastname))
        
        empl.residence = self.request.get('residence')
        empl.phone = self.request.get('phone')
        empl.date = self.request.get('date')
        empl.time = self.request.get('time')
        empl.put()
        logging.info('Data stored succesfully')        
        query_params = {'key': key.urlsafe()}
        self.redirect('/?' + urllib.urlencode(query_params))

class LinkPage(BaseHandler):
    def get(self):
        out = '\n'
        for emp in Employee.query().fetch():
            out += unicode( emp.firstname ) + ' ' + unicode( emp.lastname ) + '\n' + \
                    ' http://stromcekakodarcek.appspot.com/?key=' + emp.key.urlsafe() + '\n';
            
        logging.info(out);
        self.abort(404)

application = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/links', LinkPage),
    ], config = sessionConfig)

def main():
    # Set the logging level in the main function
    # See the section on Requests and App Caching for information on how
    # App Engine reuses your request handlers when you specify a main function
    logging.getLogger().setLevel(logging.INFO)
    

if __name__ == '__main__':
    main()