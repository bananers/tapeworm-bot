import logging
import urllib
import json
import ConfigParser as configparser

from message_handler import handle_message

# standard app engine imports
from google.appengine.api import urlfetch
import webapp2

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BASE_URL = "https://api.telegram.org/bot"

global bot

def parse_config(file="config.ini"):
    config = configparser.ConfigParser()
    config.read(file)

    return {
        'token': config.get("bot", "token"),
        'telegram_url': BASE_URL + config.get("bot", "token") + "/",
        'project_id': config.get("bot", "project_id")
    }

class RequestHandlerWithConfig(webapp2.RequestHandler):
    def initialize(self, request, response):
        super(RequestHandlerWithConfig, self).initialize(request, response)
        self.config = parse_config()

# Deserialise object and serialise it to JSON formatted string
def formatResponse(obj):
    parsed = json.load(obj)
    return json.dumps(parsed, indent=4, sort_keys=True)

def respondObj(obj):
    return json.dumps(obj, indent=4, sort_keys=True)

def sendMessage(config, payload):
    form_data = urllib.urlencode(payload)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        result = urlfetch.fetch(
            config['telegram_url'] + 'sendMessage',
            payload=form_data,
            method=urlfetch.POST,
            headers=headers
        )
    except urlfetch.Error:
        logger.exception('Caught exception sending message')

class MeHandler(RequestHandlerWithConfig):
    def get(self):
        url = self.config['telegram_url'] + "getMe"
        responseBuffer = urllib.urlopen(url)

        self.response.headers["Content-Type"] = "text/json"
        self.response.write(formatResponse(responseBuffer))

class GetUpdatesHandler(RequestHandlerWithConfig):
    def get(self):
        offset = int(self.request.get("offset", default_value="0"))
        url = self.config['telegram_url'] + "getUpdates?offset=%d" % (offset)
        responseBuffer = urllib.urlopen(url)

        self.response.headers["Content-Type"] = "text/json"
        self.response.write(formatResponse(responseBuffer))

class MessageHandler(RequestHandlerWithConfig):
    def post(self):
        logger.info("Received request: %s from %s" % (self.request.url, self.request.remote_addr))

        body = json.loads(self.request.body)
        logger.debug(body)
        if 'message' in body:
            res = handle_message(body['message'])
            logger.debug(res)
            if res is not None:
                sendMessage(self.config, res)

        self.response.status_int = 200
        self.response.write("ok")

class SetWebhookHandler(RequestHandlerWithConfig):
    def post(self):
        hook_url = "https://%s.appspot.com/webhook_%s" % (self.config['project_id'], self.config['token'])
        logger.info('Setting webhook url to %s' % hook_url)

        url = self.config['telegram_url'] + "setWebhook"
        responseBuffer = urllib.urlopen(url, urllib.urlencode({
            'url': hook_url,
            'max_connections': 2,
            'allowed_updates': ['message']
        }))

        self.response.headers["Content-Type"] = "text/json"
        self.response.write(formatResponse(responseBuffer))

class RemoveWebhookHandler(RequestHandlerWithConfig):
    def post(self):
        logger.info("Removing webhook")

        url = self.config['telegram_url'] + 'deleteWebhook'
        res = urllib.urlopen(url).read()

        self.response.headers["Content-Type"] = "text/plain"
        self.response.write(res)

class WebhookInfoHandler(RequestHandlerWithConfig):
    def get(self):
        logger.info("Getting webhook info")

        url = self.config['telegram_url'] + 'getWebhookInfo'
        res = urllib.urlopen(url)

        self.response.headers["Content-Type"] = "text/json"
        self.response.write(formatResponse(res))

config = parse_config()
app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/remove_webhook', RemoveWebhookHandler),
    ('/info_webhook', WebhookInfoHandler),
    ('/webhook_' + config['token'], MessageHandler)
], debug=True)        