import os

from aiohttp.web import run_app

from app.bot.web.app import setup_app


def main():
    app = setup_app(config_path=os.path.join(os.path.dirname(__file__), "config.yaml"))

    run_app(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
