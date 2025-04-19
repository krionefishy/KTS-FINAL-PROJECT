import base64
import logging

from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet

from app.bot.bot import Bot
from app.bot.web.config import Config, setup_config
from app.bot.web.mw import setup_middlewares
from app.store import Store, setup_store
from app.store.database.database import Database
from app.store.database.modles import Admin

from .routes import setup_routes

__all__ = ("Application",)


class Application(AiohttpApplication):
    config: Config | None = None
    store: Store | None = None
    database: Database
    bot: Bot | None = None


app = Application()


class Request(AiohttpRequest):
    admin: Admin | None = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


async def on_startup(app):
    await app.database.connect()
    app.bot = Bot(token=app.config.bot.token, app=app)
    await app.bot.start()


async def on_shutdown(app: "Application"):
    await app.database.disconnect()
    if app.bot and app.bot.poller:
        await app.bot.close()


def setup_app(config_path: str) -> Application:
    app = Application()
    logging.basicConfig(level=logging.ERROR)
    setup_config(app, config_path)
   
    # logging.getLogger().setLevel(app.config.logging.level.upper())
    
    app.database = Database(app)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)

    setup_session(
        app,
        EncryptedCookieStorage(
            secret_key,
            cookie_name=app.config.session.cookie_name,
            max_age=app.config.session.lifetime,
            httponly=app.config.session.http_only,
            secure=app.config.session.secure
        )
    )
    
    setup_aiohttp_apispec(app, title='Your game bot', swagger_path='/docs')
    setup_store(app)
    setup_middlewares(app)
    setup_routes(app)
    return app
