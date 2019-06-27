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

    def download_url_body(self, url):
        logger.debug("Downloading contents for %s", url)
        user_agent = (
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
        )
        res = requests.get(url, headers={"User-Agent": user_agent})
        res.raise_for_status()

        return res.text

    def retrieve_url_title(self, url):
        try:
            new_url = (
                f"https://{url}"
                if not (url.startswith("http://") or url.startswith("https://"))
                else url
            )
            body = self.download_url_body(new_url)
            title = self.extract_title(body)
            if title is None:
                return url
            return title
        except requests.exceptions.HTTPError:
            raise UnableToObtainTitleError


def parse_link_contents(links):
    parsed_links = []
    error_links = []

    for link in links:
        logger.debug("Finding title for %s", link)

        user_agent = (
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"
        )
        res = requests.get(link, headers={"User-Agent": user_agent})
        if res.status_code != requests.codes.ok:  # pylint: disable=no-member
            logger.debug(
                "Unable to retrieve contents of %s got %d", link, res.status_code
            )
            error_links.append((link, res.status_code))
            continue

        body = BeautifulSoup(res.text)
        title = body.title.string if body.title is not None else link
        if not title:
            title = link

        parsed_links.append({"link": link.strip(), "title": title.strip()})

    return error_links, parsed_links
