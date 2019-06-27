import pytest
import requests

import tapeworm.services as services


@pytest.mark.parametrize(
    "body,expected",
    [
        ("<html><header><title>test</title></header></html>", "test"),
        # MEGA SPACES
        (
            "<html><header>           <title>test          </title></header></html>",
            "test",
        ),
        # MEGA TABS
        (
            "<html><header>     <title>     test         </title></header></html>",
            "test",
        ),
        ("<html><header><title>😊😊😁😁🎉🎉🎁🎁✔😃🎂</title></header></html>", "😊😊😁😁🎉🎉🎁🎁✔😃🎂"),
    ],
)
def test_extract_title(body, expected):
    assert services.extract_title(body) == expected


def test_retrieve_url_title_when_no_errors(mocker):
    url = "http://hello.com"

    mocker.patch.object(services, "download_url_body")
    services.download_url_body.return_value = (
        "<html><header><title>test</title></header></html>"
    )

    assert services.retrieve_url_title(url) == "test"


def test_retrieve_url_title_when_error(mocker):
    url = "http://hello.com"

    mocker.patch.object(services, "download_url_body")
    services.download_url_body.side_effect = requests.exceptions.HTTPError

    with pytest.raises(services.UnableToObtainTitleError):
        services.retrieve_url_title(url)


def test_retrieve_title_when_title_does_not_exist(mocker):
    url = "http://hello.com"

    mocker.patch.object(services, "download_url_body")
    services.download_url_body.return_value = "<html></html>"

    assert services.retrieve_url_title(url) == url


def test_schema_is_filled_if_missing(mocker):
    url = "hello.com"

    mocker.patch.object(services, "download_url_body")

    def side_effect(*args):
        if args[0] == "https://hello.com":
            return "<html><title>hello</title></html>"
        return None

    services.download_url_body.side_effect = side_effect

    assert services.retrieve_url_title(url) == "hello"
