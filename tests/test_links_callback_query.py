import pytest

from tapeworm.model_link import Link
from .conftest import telegram_callback_query_with_data


@pytest.mark.parametrize("cq_data", [(None), ("qqq")])
def test_invalid_links_query_format(
    cq_data, incoming, telegram_callback_query_generator
):
    data = telegram_callback_query_generator()
    data["data"] = cq_data
    res = incoming.handle_data(data)

    assert res["telegram"] is None


@pytest.mark.parametrize("cq_data", [("links:n:5"), ("links:p:0")])
def test_valid_links_query_format(cq_data, incoming, telegram_callback_query_generator):
    data = telegram_callback_query_with_data(
        telegram_callback_query_generator(), cq_data
    )
    incoming.db.create_multi([Link(1, "www.test.com", "Test", "henlo", None)] * 6)
    incoming.handle_data(data)

    incoming.telegram.answer_callback_query.assert_called_once()
    incoming.telegram.edit_message_text.assert_called_once()


@pytest.mark.parametrize("data,called", [("links:n:10", False), ("links:n:0", True)])
def test_should_not_edit_when_next_returns_no_links(
    data, called, incoming, telegram_callback_query_generator
):
    """
    The purpose of this is to prevent the `No links found` message from appearing once you traversed all
    the way to the end of the links.

    This is needed since we dont track the # of links in the database since its an expensive call to count
    everytime you paginate/view links and since we don't track that, we cant write conditional logic to toggle
    the button to be a noop if its next page will be the end.
    """
    data = telegram_callback_query_with_data(telegram_callback_query_generator(), data)

    incoming.handle_data(data)

    incoming.telegram.answer_callback_query.assert_called_once()
    assert incoming.telegram.edit_message_text.called == called
