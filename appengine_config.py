import logging

from requests_toolbelt.adapters import appengine as requests_toolbelt_appengine
import google.cloud.logging


# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt_appengine.monkeypatch()

# https://cloud.google.com/appengine/docs/standard/python/how-requests-are-handled#Python_The_environment
client = google.cloud.logging.Client()
client.setup_logging()

logging.info("Stackdriver logging patched")
