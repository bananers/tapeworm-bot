# https://networklore.com/start-task-with-flask/

import logging
import threading
import time
import requests

from tapeworm import create_app

logger = logging.getLogger(__name__)
app = create_app()


@app.before_first_request
def start_update_timer():
    state = {"offset": 0}

    def check_for_messages():
        while True:
            logger.debug("Checking for new messages")

            url = app.config["TG_URL"] + f"getUpdates?offset={state['offset']}"

            logger.debug("Sending message to %s", url)
            res = requests.get(url)
            if res.status_code == 409:
                logger.debug("You need to remove the pre-existing webhook from the bot")
            else:
                body = res.json()

                if body["ok"] and body["result"]:
                    update_ids = []
                    for update in body["result"]:
                        update_ids.append(update["update_id"])
                        requests.post(
                            f"http://localhost:8080/webhook_{app.config['WEBHOOK_URL_ID']}",
                            json=update,
                        )
                    state.update(offset=max(update_ids) + 1)
            time.sleep(5)

    thread = threading.Thread(target=check_for_messages)
    thread.daemon = True
    thread.start()


def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            logger.debug("In start loop")
            try:
                r = requests.get("http://localhost:8080/")
                if r.status_code == 200:
                    logger.debug("Server started, quitting start_loop")
                    not_started = False
                logger.debug("%d", r.status_code)
            except:
                logger.debug("Server not started yet")
            time.sleep(2)

    logger.debug("Started runner")
    thread = threading.Thread(target=start_loop)
    thread.daemon = True
    thread.start()


if __name__ == "__main__":
    app.logger.setLevel(logging.DEBUG)

    start_runner()
    app.run(host="127.0.0.1", port=8080, debug=True, use_debugger=True)
