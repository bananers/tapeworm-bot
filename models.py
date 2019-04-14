from google.appengine.ext import ndb

class Link(ndb.Model):
    link = ndb.StringProperty()
    by = ndb.IntegerProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)    