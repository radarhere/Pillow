from __future__ import annotations

import io
import math
import random
from typing import cast

from . import Image, ImageFilter


def _lcd_resampling(img: Image.Image) -> Image.Image:
    """
    Simulate an LCD display by mapping each pixel to a single RGB subpixel
    in the repeating R-G-B stripe layout.

    :param img:
    :return: An image.
    """
    resampled_img = Image.new("RGB", img.size)

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = cast("tuple[int, int, int]", img.getpixel((x, y)))
            resampled_img.putpixel((x, y), ((r, 0, 0), (0, g, 0), (0, 0, b))[x % 3])

    return resampled_img


def _projective_transformation(img: Image.Image) -> Image.Image:
    """
    Apply a random projective transformation to simulate varying camera
    position and orientation relative to the display.

    :param img:
    :return: An image.
    """
    theta = math.radians(random.uniform(-1, 1))

    # rotation
    a = math.cos(theta)
    b = -math.sin(theta)
    d = math.sin(theta)
    e = math.cos(theta)

    # Translation
    c = random.uniform(-0.01 * img.width, 0.01 * img.width)
    f = random.uniform(-0.01 * img.height, 0.01 * img.height)

    # Perspective distortion
    g = random.uniform(-1e-5, 1e-5)
    h_p = random.uniform(-1e-5, 1e-5)

    # H
    coeffs = (a, b, c, d, e, f, g, h_p)

    return img.transform(
        img.size, Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC
    )


def _radial_distortion(img: Image.Image, k: float = -1e-7) -> Image.Image:
    """
    Use radial distortion function to simulate lens distortion

    :param img:
    :param k:
    :return: An image
    """
    radial_distort = Image.new("RGB", img.size)
    w, h = img.size

    cx = w / 2
    cy = h / 2

    for y in range(h):
        for x in range(w):
            r, g, b = cast("tuple[int, int, int]", img.getpixel((x, y)))
            xc = x - cx
            yc = y - cy
            radius2 = xc**2 + yc**2

            factor = 1 + k * radius2
            radial_x = int(xc * factor + cx)
            radial_y = int(yc * factor + cy)

            # Boundary check
            if 0 <= radial_x < w and 0 <= radial_y < h:
                radial_distort.putpixel((radial_x, radial_y), (r, g, b))

    return radial_distort


def _flat_top_kernel(
    size: int = 5, sigma: float = 1.0, n: int = 2
) -> list[list[float]]:
    """
    Generate a flat-top Gaussian kernel.

    :param size: the size of the kernel to be produced
    :param sigma: controls the broadness of the Gaussian kernel
    :param n: controls the flatness of the kernel peak
    :return: An array
    """
    kernel = []
    center = size // 2
    total = 0.0

    for y in range(size):
        row = []
        for x in range(size):
            dx = x - center
            dy = y - center
            r2 = dx * dx + dy * dy
            value = math.exp(-((r2 / (2 * sigma * sigma)) ** n))
            row.append(value)
            total += value
        kernel.append(row)

    for y in range(size):
        for x in range(size):
            kernel[y][x] /= total

    return kernel


def _flat_top_filtering(
    img: Image.Image, size: int = 5, sigma: float = 1.0, n: int = 2
) -> Image.Image:
    """
    Applying the flat top gaussian kernel on the image to simulate anti-aliasing fiter

    :param img:
    :param size:
    :param sigma:
    :param n:
    :return: An image
    """
    kernel = _flat_top_kernel(size, sigma, n)
    flat_kernel = [value for row in kernel for value in row]

    return img.filter(ImageFilter.Kernel((5, 5), flat_kernel, scale=1))


def _bayer_resampling(img: Image.Image) -> None:
    """
    Simulate a Bayer CFA (GRBG) where each pixel only captures one color channel

    :param img:
    """
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = cast("tuple[int, int, int]", img.getpixel((x, y)))
            if y % 2 == 0:
                if x % 2 == 0:
                    value = (0, g, 0)
                else:
                    value = (r, 0, 0)
            else:
                if x % 2 == 0:
                    value = (0, 0, b)
                else:
                    value = (0, g, 0)
            img.putpixel((x, y), value)


def _add_noise(img: Image.Image) -> None:
    """
    Add standard normal noise to the image to simulate sensor noise

    :param img:
    """
    for y in range(img.height):
        for x in range(img.width):
            value = cast("tuple[int, int, int]", img.getpixel((x, y)))
            img.putpixel((x, y), tuple(int(v + random.gauss(0, 1)) for v in value))


def _clamp(v: int, lo: int, hi: int) -> int:
    return lo if v < lo else (hi if v > hi else v)


def _get_channel(img: Image.Image, x: int, y: int, ch: int, w: int, h: int) -> int:
    x = _clamp(x, 0, w - 1)
    y = _clamp(y, 0, h - 1)
    return cast("tuple[int, int, int]", img.getpixel((x, y)))[ch]


def _demosaic_bilinear(img: Image.Image) -> None:
    """
    Reconstruct the full RGB image from the Bayer CFA image using bilinear interpolation
    of the other 2 remaining channels from nearby pixels at each pixel

    :param img:
    """
    w, h = img.size
    for y in range(h):
        for x in range(w):
            pixel = cast("tuple[int, int, int]", img.getpixel((x, y)))

            if y % 2 == 0 and x % 2 == 0:
                new_r = (
                    _get_channel(img, x - 1, y, 0, w, h)
                    + _get_channel(img, x + 1, y, 0, w, h)
                ) >> 1
                new_g = pixel[1]
                new_b = (
                    _get_channel(img, x, y - 1, 2, w, h)
                    + _get_channel(img, x, y + 1, 2, w, h)
                ) >> 1

            elif y % 2 == 0 and x % 2 == 1:
                new_r = pixel[0]
                new_g = (
                    _get_channel(img, x - 1, y, 1, w, h)
                    + _get_channel(img, x + 1, y, 1, w, h)
                    + _get_channel(img, x, y - 1, 1, w, h)
                    + _get_channel(img, x, y + 1, 1, w, h)
                ) >> 2
                new_b = (
                    _get_channel(img, x - 1, y - 1, 2, w, h)
                    + _get_channel(img, x + 1, y - 1, 2, w, h)
                    + _get_channel(img, x - 1, y + 1, 2, w, h)
                    + _get_channel(img, x + 1, y + 1, 2, w, h)
                ) >> 2

            elif y % 2 == 1 and x % 2 == 0:
                new_r = (
                    _get_channel(img, x - 1, y - 1, 0, w, h)
                    + _get_channel(img, x + 1, y - 1, 0, w, h)
                    + _get_channel(img, x - 1, y + 1, 0, w, h)
                    + _get_channel(img, x + 1, y + 1, 0, w, h)
                ) >> 2
                new_g = (
                    _get_channel(img, x - 1, y, 1, w, h)
                    + _get_channel(img, x + 1, y, 1, w, h)
                    + _get_channel(img, x, y - 1, 1, w, h)
                    + _get_channel(img, x, y + 1, 1, w, h)
                ) >> 2
                new_b = pixel[2]

            else:
                new_r = (
                    _get_channel(img, x, y - 1, 0, w, h)
                    + _get_channel(img, x, y + 1, 0, w, h)
                ) >> 1
                new_g = pixel[1]
                new_b = (
                    _get_channel(img, x - 1, y, 2, w, h)
                    + _get_channel(img, x + 1, y, 2, w, h)
                ) >> 1

            img.putpixel(
                (x, y),
                tuple(_clamp(value, 0, 255) for value in (new_r, new_g, new_b)),
            )


def _denoise(img: Image.Image) -> Image.Image:
    return img.filter(ImageFilter.GaussianBlur(radius=1))


def _jpeg_compression(img: Image.Image) -> Image.Image:
    buffer = io.BytesIO()
    img.save(buffer, "JPEG")

    return Image.open(buffer)
