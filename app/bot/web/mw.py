import typing

if typing.TYPE_CHECKING:
    from app.bot.web.app import Application

import json
import logging

from aiohttp import web
from aiohttp.abc import Request
from aiohttp.web_exceptions import HTTPException, HTTPUnprocessableEntity

from app.pkg.utils import error_json_response

logging.basicConfig(level=logging.INFO)

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


@web.middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        return await handler(request)

    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
            data=json.loads(e.text),
        )
    except HTTPException as e:
        status_code = e.status_code

        try:
            error_data = json.loads(e.text)
        except:
            error_data = {"message": e.reason}
        logging.error(f"occured an error {e}, code {status_code}, err_data {error_data}")
        return error_json_response(
            http_status=status_code,
            status=HTTP_ERROR_CODES.get(status_code, "unknown_error"),
            message=e.reason,
            data=error_data,
        )
    except Exception as e:
        logging.error(f"occured an error {e}")
        return error_json_response(http_status=500, status=HTTP_ERROR_CODES[500], message=str(e), data={})


def setup_middlewares(app: "Application"):
    app.middlewares.append(error_handling_middleware)
