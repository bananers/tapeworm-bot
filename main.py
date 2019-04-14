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
        'telegram_url': BASE_URL + config.get("bot", "token") + "/"
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

def sendMessage(config, message, chat_id):
    params = {
        "chat_id": chat_id,
        "text": message.encode("utf-8")
    }

    resp = urllib.urlopen(config["telegram_url"] + "sendMessage", urllib.urlencode(params)).read()

class MeHandler(RequestHandlerWithConfig):
    def get(self):
        url = self.config['telegram_url'] + "getMe"
        responseBuffer = urllib.urlopen(url)

        self.response.headers["Content-Type"] = "text/json"
        self.response.write(formatResponse(responseBuffer))

class GetUpdatesHandler(RequestHandlerWithConfig):
    def get(self):
        url = self.config['telegram_url'] + "getUpdates"
        responseBuffer = urllib.urlopen(url)

        self.response.headers["Content-Type"] = "text/json"
        self.response.write(formatResponse(responseBuffer))

class MessageHandler(RequestHandlerWithConfig):
    def post(self):
        logger.info("Received request: %s from %s" % (self.request.url, self.request.remote_addr))

        body = json.loads(self.request.body)
        res = handle_message(body['message'])
        if res is None:
            logger.debug("Skipping messaging, res is None")
            return
            
        sendMessage(self.config, res['text'], res['chat_id'])

        self.response.headers["Content-Type"] = "text/json"
        self.response.write(respondObj(res))

config = parse_config()
app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/webhook_' + config['token'], MessageHandler)
], debug=True)        