from dataclasses import dataclass
from bs4 import BeautifulSoup


@dataclass
class Location:
    lat: float
    lon: float


def read_kml_file(kml_file: str) -> list[str]:
    with open(kml_file) as fp:
        soup = BeautifulSoup(fp, "lxml-xml")
        str_arr = [x.strip() for x in soup.coordinates.contents[0].splitlines()]
        return list(filter(None, str_arr))


def parse_kml_file(coordinates: list[str]) -> list[Location]:
    locations = []
    for coordinate in coordinates:
        lon, lat, _ = coordinate.split(",")
        locations.append(Location(float(lat), float(lon)))
    return locations
