"""Test DdsImagePlugin"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest

from PIL import DdsImagePlugin, Image

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    assert_image_similar_tofile,
    hopper,
    timeout_unless_slower_valgrind,
)

TEST_FILE_DXT1 = "Tests/images/dxt1-rgb-4bbp-noalpha_MipMaps-1.dds"
TEST_FILE_DXT3 = "Tests/images/dxt3-argb-8bbp-explicitalpha_MipMaps-1.dds"
TEST_FILE_DXT5 = "Tests/images/dxt5-argb-8bbp-interpolatedalpha_MipMaps-1.dds"
TEST_FILE_ATI1 = "Tests/images/ati1.dds"
TEST_FILE_ATI2 = "Tests/images/ati2.dds"
TEST_FILE_DX10_BC4_TYPELESS = "Tests/images/bc4_typeless.dds"
TEST_FILE_DX10_BC4_UNORM = "Tests/images/bc4_unorm.dds"
TEST_FILE_DX10_BC5_TYPELESS = "Tests/images/bc5_typeless.dds"
TEST_FILE_DX10_BC5_UNORM = "Tests/images/bc5_unorm.dds"
TEST_FILE_DX10_BC5_SNORM = "Tests/images/bc5_snorm.dds"
TEST_FILE_DX10_BC1 = "Tests/images/bc1.dds"
TEST_FILE_DX10_BC1_TYPELESS = "Tests/images/bc1_typeless.dds"
TEST_FILE_BC4U = "Tests/images/bc4u.dds"
TEST_FILE_BC5S = "Tests/images/bc5s.dds"
TEST_FILE_BC5U = "Tests/images/bc5u.dds"
TEST_FILE_BC6H = "Tests/images/bc6h.dds"
TEST_FILE_BC6HS = "Tests/images/bc6h_sf.dds"
TEST_FILE_DX10_BC7 = "Tests/images/bc7-argb-8bpp_MipMaps-1.dds"
TEST_FILE_DX10_BC7_UNORM_SRGB = "Tests/images/DXGI_FORMAT_BC7_UNORM_SRGB.dds"
TEST_FILE_DX10_R8G8B8A8 = "Tests/images/argb-32bpp_MipMaps-1.dds"
TEST_FILE_DX10_R8G8B8A8_UNORM_SRGB = "Tests/images/DXGI_FORMAT_R8G8B8A8_UNORM_SRGB.dds"
TEST_FILE_UNCOMPRESSED_L = "Tests/images/uncompressed_l.dds"
TEST_FILE_UNCOMPRESSED_L_WITH_ALPHA = "Tests/images/uncompressed_la.dds"
TEST_FILE_UNCOMPRESSED_RGB = "Tests/images/hopper.dds"
TEST_FILE_UNCOMPRESSED_BGR15 = "Tests/images/bgr15.dds"
TEST_FILE_UNCOMPRESSED_RGB_WITH_ALPHA = "Tests/images/uncompressed_rgb.dds"


@timeout_unless_slower_valgrind(1)
@pytest.mark.parametrize(
    "test_file",
    [
        "Tests/images/timeout-041dd17dfde800360a47a172269df127af138c6b.dds",
    ],
)
def test_timeout(test_file) -> None:
    with Image.open(test_file) as im:
        im.load()
