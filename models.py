from google.cloud import datastore

class Link(ndb.Model):
    link = ndb.StringProperty()
    title = ndb.StringProperty()
    by = ndb.IntegerProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)    

    @classmethod
    def query_all(cls):
        return cls.query().order(-cls.date)