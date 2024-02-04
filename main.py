from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

from module.compare import check_for_duplicates
from module.convert import convert360, get_image_paths, rename_files
from module.download import get_panorama
from module.parse_kml import read_kml_file, parse_kml_file, Location
from module.search import search_panoramas, Panorama

import asyncio
import os


async def convert_files() -> None:
    if not os.path.exists(CONVERSION_LOCATION):
        os.makedirs(CONVERSION_LOCATION)

    files = get_image_paths(DOWNLOAD_LOCATION)
    await tqdm_asyncio.gather(*[convert360(f'{DOWNLOAD_LOCATION}/{file}', f'{CONVERSION_LOCATION}/{file}') for file in files])


def remove_copies() -> None:
    res = set()
    for file in check_for_duplicates([DOWNLOAD_LOCATION]):
        f = file.split('\\')
        res.add(f[len(f) - 1])

    for file in res:
        os.remove(f'{DOWNLOAD_LOCATION}/{file}')


def load_files() -> list[Location]:
    coordinates = read_kml_file(KML_FILE)
    return parse_kml_file(coordinates)


async def download_data(locations: list[Location]) -> list[Panorama]:
    panoramas = await search_panoramas(locations)
    return [panorama for panorama in panoramas if panorama]


async def download_images(panoramas: list[Panorama], start: int = 0, stop: int = None, skip: list[int] = []) -> None:
    if stop is None:
        stop = len(panoramas)
    if not os.path.exists(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)

    with tqdm(panoramas) as pbar:
        for i, panorama in enumerate(panoramas):
            if start < i < stop and i not in skip:
                await get_panorama(panorama.pano_id, DOWNLOAD_LOCATION, i)
            pbar.update(1)


async def main(skip_download: bool = False, skip_conversion: bool = False, skip_remove_copies: bool = False) -> None:
    if not skip_download:
        locations = load_files()
        panoramas = await download_data(locations)
        await download_images(panoramas)

    if not skip_conversion:
        await convert_files()

    if not skip_remove_copies:
        remove_copies()

    rename_files(DOWNLOAD_LOCATION)


if __name__ == '__main__':
    DOWNLOAD_LOCATION = 'route-1'
    CONVERSION_LOCATION = 'convert'
    KML_FILE = "route.kml"

    args = {"skip_download": False, "skip_conversion": True, "skip_remove_copies": False}

    asyncio.run(main(**args))
