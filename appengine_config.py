from requests_toolbelt.adapters import appengine as requests_toolbelt_appengine

# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt_appengine.monkeypatch()