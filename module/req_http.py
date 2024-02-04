"""
http get methods using request and Modified for concurrency.
from https://github.com/ArjanCodes/2022-asyncio/blob/main/req_http.py
"""

from requests import Response
import requests
import asyncio


def http_get_sync(url: str, **kwargs) -> Response:
    response = requests.get(url, **kwargs)
    return response


async def http_get(url: str, **kwargs) -> Response:
    return await asyncio.to_thread(http_get_sync, url, **kwargs)
