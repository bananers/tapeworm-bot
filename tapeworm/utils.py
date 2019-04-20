import configparser

from bs4 import BeautifulSoup

def parse_config(telegram_base_url, file="config.ini"):
    config = configparser.ConfigParser()
    config.read(file)

    return {
        'token': config.get("bot", "token"),
        'telegram_url': telegram_base_url + config.get("bot", "token") + "/",
        'project_id': config.get("bot", "project_id"),
        'webhook_url_id': config.get("bot", "webhook_url_id")
    }

