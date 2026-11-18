"""
pytest-benchmark tests for Pillow features.
"""

from __future__ import annotations

import hashlib
import os
import re
import warnings
from importlib.util import find_spec
from io import BytesIO
from pathlib import Path

import pytest

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageMath
from PIL.Image import Resampling, Transform, Transpose

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from _pytest.mark.structures import ParameterSet
    from pytest_benchmark.fixture import (  # type: ignore[unused-ignore, import-not-found]
        BenchmarkFixture,
    )

    BenchmarkSave = Callable[[Image.Image], None]


if not (find_spec("pytest_benchmark") or find_spec("pytest_codspeed")):
    pytest.skip("pytest-benchmark or pytest-codspeed required", allow_module_level=True)

IMAGES_PATH = Path(__file__).parent / "images"

_save_results = os.environ.get("PILLOW_BENCHMARK_SAVE_RESULTS_PATH")
SAVE_RESULTS_PATH = Path(_save_results) if _save_results else None

# These can be adjusted to add more modes to benchmark
# (however all features benchmarked might not support all PIL modes).
MODES = ["RGB", "RGBA", "L", "LA"]

# The size for generated test images.
# Note that adjusting this will naturally change how long operations take.
# The `bench` fixture takes care of saving this information in the extra info
# for the benchmark run, so that throughput (Mpx/s) can be recomputed in the future.
SIZES = [(1237, 811)]  # Primes, non-power-of-two, asymmetric, approximately 1024x1024

# For benchmarks that act on test fixture files, these are the paths loaded.
IMAGES_PATH = Path(__file__).parent / "images"

# These are derived from the other configuration, above.
RGB_MODES = [mode for mode in MODES if mode.startswith("RGB")]
ALPHA_MODES = [mode for mode in MODES if mode.endswith("A")]
SCALE_MODES = [*MODES, "I", "F"]


def _format_size(size: tuple[int, int]) -> str:
    return f"{size[0]}x{size[1]}"


def _format_path(path: Path) -> str:
    return path.name


@pytest.fixture
def bench(
    request: pytest.FixtureRequest,
    benchmark: BenchmarkFixture,
) -> BenchmarkFixture:
    """
    pytest-benchmark with extra information.
    """
    try:
        benchmark.extra_info["mode"] = request.getfixturevalue("mode")
    except LookupError:
        pass
    try:
        size = request.getfixturevalue("size")
        benchmark.extra_info["size"] = _format_size(size)
        benchmark.extra_info["pixels"] = size[0] * size[1]
    except LookupError:
        pass
    return benchmark


@pytest.fixture
def benchmark_save(request: pytest.FixtureRequest) -> BenchmarkSave:
    """
    Fixture to save a benchmark image, if so configured.
    """

    def save(im: Image.Image) -> None:
        if SAVE_RESULTS_PATH:
            safe_name = re.sub("[^-a-zA-Z0-9]", "_", str(request.node.name))
            name = (SAVE_RESULTS_PATH / safe_name).with_suffix(".png")
            try:
                SAVE_RESULTS_PATH.mkdir(parents=True, exist_ok=True)
                im.save(name)
            except Exception as e:
                warnings.warn(
                    f"Failed to save benchmark result to {name}: {e}",
                    stacklevel=2,
                )

    return save


def make_pillow_image(
    mode: str,
    size: tuple[int, int],
    seed: int = 0,
) -> Image.Image:
    """
    Generate a synthetic test image with the given mode and size.
    Different seeds give different final images.
    """
    width, height = size
    vertical = Image.linear_gradient("L")
    horizontal = vertical.transpose(Transpose.ROTATE_90)
    radial = Image.radial_gradient("L")
    base = Image.merge("RGB", (horizontal, vertical, radial)).resize(
        size, Resampling.BILINEAR
    )
    # SHAKE128 gives us a predictable noise pattern.
    noise_bytes = hashlib.shake_128(f"pillow-benchmark-{seed}".encode()).digest(
        width * height * 3
    )
    noise = Image.frombytes("RGB", size, noise_bytes)

    def centered_box(area_fraction: float) -> tuple[int, int, int, int]:
        inset = (1 - area_fraction**0.5) / 2
        return (
            round(width * inset),
            round(height * inset),
            round(width * (1 - inset)),
            round(height * (1 - inset)),
        )

    im = base
    noise_box = centered_box(1 / 2)
    im.paste(noise.crop(noise_box), noise_box)  # Noise in the middle
    im.paste(tuple(noise_bytes[:3]), centered_box(1 / 6))  # Solid center
    if seed:
        im = ImageChops.offset(im, seed * 383, seed * 271)
    return im.convert(mode)


BBOX_SCENARIOS: dict[str, tuple[float, str] | None] = {
    "half-centered": (0.5, "center"),
    "small-centered": (0.1, "center"),
    "half-corner": (0.5, "corner"),
    "empty": None,
}


def make_bbox_image(
    mode: str,
    size: tuple[int, int],
    region: tuple[float, str] | None,
) -> Image.Image:
    im = Image.new(mode, size, 0)
    if region is None:
        return im
    fraction, placement = region
    w, h = size
    bw, bh = max(1, round(w * fraction)), max(1, round(h * fraction))
    if placement == "center":
        left, top = (w - bw) // 2, (h - bh) // 2
    else:
        left, top = w - bw, h - bh
    nbands = len(im.getbands())
    color = (255, 128, 64, 255)[:nbands] if nbands > 1 else 255
    im.paste(color, (left, top, left + bw - 1, top + bh - 1))
    return im


@pytest.mark.benchmark(group="composition")
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("size", SIZES, ids=_format_size)
def test_blend(
    bench: BenchmarkFixture,
    mode: str,
    size: tuple[int, int],
) -> None:
    im1 = make_pillow_image(mode, size)
    im2 = make_pillow_image(mode, size, seed=1)
    result = bench(Image.blend, im1, im2, 0.5)
    assert result.size == im1.size
