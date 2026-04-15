from __future__ import annotations

import logging
import math
from pathlib import Path

import numpy as np
import tifffile


logging.getLogger("tifffile").setLevel(logging.ERROR)


def open_geotiff(path: Path) -> tuple[np.ndarray, dict[str, float], float | None]:
    with tifffile.TiffFile(path) as tif:
        page = tif.pages[0]
        array = page.asarray()
        nodata = extract_nodata(page)
        scale = page.tags["ModelPixelScaleTag"].value
        tie = page.tags["ModelTiepointTag"].value
        georef = {
            "x0": float(tie[3]),
            "y0": float(tie[4]),
            "pixel_width": float(scale[0]),
            "pixel_height": float(scale[1]),
            "width": int(page.imagewidth),
            "height": int(page.imagelength),
        }
    return array, georef, nodata


def extract_nodata(page: tifffile.TiffPage) -> float | None:
    if "GDAL_NODATA" in page.tags:
        try:
            return float(page.tags["GDAL_NODATA"].value)
        except Exception:
            return None
    return None


def sample_value(
    array: np.ndarray,
    georef: dict[str, float],
    longitude: float,
    latitude: float,
    nodata: float | None,
    fallback_radius: int = 1,
) -> tuple[float, bool]:
    col = int((longitude - georef["x0"]) / georef["pixel_width"])
    row = int((georef["y0"] - latitude) / georef["pixel_height"])

    if row < 0 or col < 0 or row >= georef["height"] or col >= georef["width"]:
        return float("nan"), False

    value = float(array[row, col])
    if is_invalid(value, nodata):
        radius = max(1, int(fallback_radius))
        row_start = max(0, row - radius)
        row_end = min(georef["height"], row + radius + 1)
        col_start = max(0, col - radius)
        col_end = min(georef["width"], col + radius + 1)
        window = array[row_start:row_end, col_start:col_end]
        valid = [float(item) for item in window.flatten() if not is_invalid(float(item), nodata)]
        if not valid:
            return float("nan"), True
        return float(sum(valid) / len(valid)), True
    return value, False


def is_invalid(value: float, nodata: float | None) -> bool:
    if math.isnan(value):
        return True
    if nodata is not None and value == nodata:
        return True
    return False
