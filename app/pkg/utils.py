from aiohttp.web import json_response as aiohttp_json_responce
from aiohttp.web_response import Response


def json_responce(data: dict | None = None) -> Response:
    if data is None:
        data = {}

    return aiohttp_json_responce(
        data={
        "data": data,
        }
    )


def error_json_responce(
        http_status: int, 
        status: str,
        message: str | None = None,
        data: dict | None = None
):
    return aiohttp_json_responce(
        data={
            "status": status,
            "message": message,
            "data": data
        },
        status=http_status
    )
    