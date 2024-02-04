from aiodecorators import Semaphore
from natsort import natsorted
from PIL import Image

import numpy as np
import py360convert
import asyncio
import os

Image.MAX_IMAGE_PIXELS = None


def get_image_paths(folder: str, extension: str = "jpg") -> list[str]:
    files = []
    for file in os.listdir(folder):
        if file.endswith(extension):
            files.append(file)
    return natsorted(files)


def convert360_sync(file: str, save: str) -> None:
    cube_dice = np.array(Image.open(file))
    out = py360convert.e2p(cube_dice, (90, 90), 35, 0, (1000, 1000))
    Image.fromarray(out.astype(np.uint8)).save(save)


def rename_files(folder: str) -> None:
    files = get_image_paths(folder)
    for i, file in enumerate(files):
        os.rename(f'{folder}/{file}', f'{folder}/image-{i}.jpg')


@Semaphore(10)
async def convert360(file: str, save: str) -> None:
    await asyncio.to_thread(convert360_sync, file, save)
