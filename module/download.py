"""
download panorama from Google street view
google-streetview 1.2.9 https://pypi.org/project/google-streetview/
Modified the files to all for concurrency for faster download performance.
"""

from dataclasses import dataclass
from typing import Tuple
from PIL import Image
from io import BytesIO

from module.req_http import http_get

import time
import itertools
import requests
import asyncio


@dataclass
class TileInfo:
    x: int
    y: int
    fileURL: str


@dataclass
class Tile:
    x: int
    y: int
    image: Image.Image


def get_width_and_height_from_zoom(zoom: int) -> Tuple[int, int]:
    return 2 ** zoom, 2 ** (zoom - 1)


def make_download_url(pano_id: str, zoom: int, x: int, y: int) -> str:
    return f'https://cbk0.google.com/cbk?output=tile&panoid={pano_id}&zoom={zoom}&x={x}&y={y}'


async def fetch_panorama_tile(tile_info: TileInfo) -> Image.Image:
    try:
        response = await http_get(tile_info.fileURL, stream=True)
        return Image.open(BytesIO(response.content))
    except requests.ConnectionError:
        print("Connection error. Trying again in 2 seconds.")
        time.sleep(2)
        return await fetch_panorama_tile(tile_info)


def get_tile_info(pano_id: str, zoom: int) -> list[TileInfo]:
    tile_info = []
    width, height = get_width_and_height_from_zoom(zoom)
    for x, y in itertools.product(range(width), range(height)):
        url = make_download_url(pano_id=pano_id, zoom=zoom, x=x, y=y)
        info = TileInfo(x=x, y=y, fileURL=url)
        tile_info.append(info)
    return tile_info


async def get_tiles(pano_id: str, zoom: int) -> list[Tile]:
    tile_info = get_tile_info(pano_id, zoom)
    images = await asyncio.gather(*[fetch_panorama_tile(info) for info in tile_info])

    tiles = []
    for i, info in enumerate(tile_info):
        tile = Tile(x=info.x, y=info.y, image=images[i])
        tiles.append(tile)
    return tiles


async def get_panorama(pano_id: str, destination: str, index: int, zoom: int = 5) -> None:
    tile_width = 512
    tile_height = 512

    total_width, total_height = get_width_and_height_from_zoom(zoom)
    panorama = Image.new("RGB", (total_width * tile_width, total_height * tile_height))

    tiles = await get_tiles(pano_id=pano_id, zoom=zoom)

    for tile in tiles:
        panorama.paste(im=tile.image, box=(tile.x * tile_width, tile.y * tile_height))
        del tile

    panorama.save(f'{destination}/image-{index}.jpg', "jpeg")
    del panorama
