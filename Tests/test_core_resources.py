from __future__ import annotations

import sys

import pytest

from PIL import Image

from .helper import running_in_another_thread, is_pypy


class TestCoreMemory:
    def teardown_method(self) -> None:
        # Restore default values
        Image.core.set_alignment(1)
        Image.core.set_block_size(1024 * 1024)
        Image.core.set_blocks_max(0)
        Image.core.clear_cache()

    def test_set_alignment(self) -> None:
        if running_in_another_thread():
            return
        print("torch only once")
        for i in [1, 2, 4, 8, 16, 32]:
            Image.core.set_alignment(i)
            alignment = Image.core.get_alignment()
            assert alignment == i

            # Try to construct new image
            Image.new("RGB", (10, 10))
