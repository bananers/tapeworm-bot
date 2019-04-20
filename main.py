import logging

from tapeworm import create_app

app = create_app()

if __name__ == "__main__":
    app.logger.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='127.0.0.1', port=8080, debug=True, use_debugger=True)