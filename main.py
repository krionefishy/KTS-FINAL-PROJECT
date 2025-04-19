import os

from aiohttp.web import run_app

from app.bot.web.app import setup_app

if __name__ == "__main__":
    app = setup_app(
        config_path=os.path.join(os.path.dirname(__file__), "config.yaml")
    )

    run_app(app, host="127.0.0.1")

