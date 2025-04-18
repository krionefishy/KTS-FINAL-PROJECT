from app.bot.web.app import setup_app
import os

from aiohttp.web import run_app


if __name__ == "__main__":
    app = setup_app(
        config_path=os.path.join(os.path.dirname(__file__), "config.yaml")
    )
    print("апп засетапили")

    run_app(app)

