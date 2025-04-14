import typing

if typing.TYPE_CHECKING:
    from app.bot.web.app import Application

from aiohttp import web
from aiohttp.abc import Request
from aiohttp.web_exceptions import HTTPException
import logging 
logging.basicConfig(level=logging.INFO)



HTTP_ERROR_CODES = {
    400: "bad_request",
    403: "forbidden",
    404: "not found",
    409: "conflict"
}

@web.middleware
async def error_handling_mw(request: Request, handler):

    try: 
        return await handler(request)
    except Exception as e:
        logging.error(msg = f"Occured an error: {type(e)}")



def setup_middlewares(app: "Application"):
    app.middlewares.append(error_handling_mw)