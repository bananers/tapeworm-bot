import pytest

from .conftest import telegram_callback_query_with_data


@pytest.mark.parametrize("cq_data", [(None), ("qqq")])
def test_invalid_links_query_format(
    cq_data, incoming, telegram_callback_query_generator
):
    data = telegram_callback_query_generator()
    data["data"] = cq_data
    res = incoming.handle_data(data)

    assert res["telegram"] is None


@pytest.mark.parametrize("cq_data", [("links:n:10"), ("links:p:0")])
def test_valid_links_query_format(cq_data, incoming, telegram_callback_query_generator):
    data = telegram_callback_query_with_data(
        telegram_callback_query_generator(), cq_data
    )

    incoming.handle_data(data)

    incoming.telegram.answer_callback_query.assert_called_once()
    incoming.telegram.edit_message_text.assert_called_once()
