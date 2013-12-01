import os
import re
import logging
import jinja2
import webapp2
from model import Employee
from util import BaseHandler, sessionConfig
from google.appengine.ext import ndb


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
    


ERROR_NOT_ENTERED = u'Zabudli ste vyplniť pole %s'
ERROR_WRONG_PHONE = u'Nesprávne telefónne číslo. Povolené znaky sú: +, -, 0-9, /, \, medzera'

labels = {
         'residence' : u'Adresa',
         'phone' : u'Telefónne číslo',
         'date' : u'Dátum doručenia',
         'time' : u'Čas doručenia', 
}

def getUnenteredMsg( value ):
    return ERROR_NOT_ENTERED % (labels[ value ],)


def createTestEmployee():
    empl = Employee()
    empl.firstname = 'jozko'
    empl.lastname = 'mrkvicka'
    empl.put()
    
class MainPage(BaseHandler):

    def displayPage(self, params, errors=[], errorIds=[]):
        template_values = {
            'p': params,
            'errors': errors,
            'errorIds': errorIds,
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
        self.displayPage( empl )        
        
       
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
        errors, errorIds = self.validateData() 
        if errors:
            self.displayPage( self.request.params, errors, errorIds )
            return        
        
        logging.info('POST DB Key: ' + self.session.get('key'))
        key = ndb.Key( urlsafe = self.session.get('key'))
        empl = key.get()
        logging.info('Successfull POST employee: ' + unicode(empl.firstname) + ' ' + unicode(empl.lastname))
        
        empl.residence = self.request.get('residence')
        empl.phone = self.request.get('phone')
        empl.date = self.request.get('date')
        empl.time = self.request.get('time')
        empl.put()
        logging.info('Data stored succesfully')        
        self.redirect('/results')
        
class ResultPage(BaseHandler):
            
    def get(self):
        template_values = { 
        }
        template = JINJA_ENVIRONMENT.get_template('results.html')
        self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/results', ResultPage),
    ], config = sessionConfig)

def main():
    # Set the logging level in the main function
    # See the section on Requests and App Caching for information on how
    # App Engine reuses your request handlers when you specify a main function
    logging.getLogger().setLevel(logging.INFO)
    

if __name__ == '__main__':
    main()