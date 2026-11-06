"""Accumulate a TCP byte stream until the known frame size is reached."""

from __future__ import annotations


class FrameReassembly:
    """No magic, no length prefix, no dtype, no shape, no timestamp, no name."""

    def __init__(self, frame_size: int) -> None:
        if frame_size <= 0:
            raise ValueError("frame size must be the known byte count")
        self._frame_size = frame_size
        self._buffer = bytearray()

    @property
    def frame_size(self) -> int:
        return self._frame_size

    def read_frame(self, reader: object) -> bytes:
        read = getattr(reader, "read", None)
        if not callable(read):
            raise TypeError("reader must provide read(size)")
        while len(self._buffer) < self._frame_size:
            chunk = read(self._frame_size - len(self._buffer))
            if not chunk:
                raise ConnectionError("stream ended before the exact frame byte count")
            if not isinstance(chunk, (bytes, bytearray)):
                raise TypeError("reader.read must return bytes")
            self._buffer.extend(chunk)
        frame = bytes(self._buffer[: self._frame_size])
        del self._buffer[: self._frame_size]
        return frame
