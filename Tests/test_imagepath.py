from __future__ import annotations

import struct

import pytest

from PIL import Image


def test_overflow_segfault() -> None:
    # Some Pythons fail getting the argument as an integer, and it falls
    # through to the sequence. Seeing this on 32-bit Windows.
    if True:#with pytest.raises((TypeError, MemoryError)):
        # post patch, this fails with a memory error
        x = Evil()

        # This fails due to the invalid malloc above,
        # and segfaults
        for i in range(200000):
            x[i] = b"0" * 16


class Evil:
    def __init__(self) -> None:
        print("python value", 0x4000000000000000)
        self.corrupt = Image.core.path(0x4000000000000000)

    def __getitem__(self, i: int) -> bytes:
        x = self.corrupt[i]
        return struct.pack("dd", x[0], x[1])

    def __setitem__(self, i: int, x: bytes) -> None:
        self.corrupt[i] = struct.unpack("dd", x)
