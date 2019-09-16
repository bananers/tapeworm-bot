import logging
import requests

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class UnableToObtainTitleError(Exception):
    pass


class TitleExtractor:
    def extract_title(self, body: str):
        body = BeautifulSoup(body, features="html.parser")
        return body.title.string.strip() if body.title is not None else None

    def download_url_body(self, url) -> (str, str):
        logger.debug("Downloading contents for %s", url)
        user_agent = (
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
        )
        res = requests.get(url, headers={"User-Agent": user_agent})
        res.raise_for_status()

        return (res.text, res.url)

    def retrieve_url_title(self, url) -> (str, str):
        try:
            new_url = (
                f"https://{url}"
                if not (url.startswith("http://") or url.startswith("https://"))
                else url
            )
            (body, req_url) = self.download_url_body(new_url)
            title = self.extract_title(body)
            if title is None:
                return req_url
            return (title, req_url)
        except requests.exceptions.HTTPError:
            raise UnableToObtainTitleError
