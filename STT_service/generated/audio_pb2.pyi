from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AudioChunk(_message.Message):
    __slots__ = ("audio_data", "timestamp")
    AUDIO_DATA_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    audio_data: bytes
    timestamp: int
    def __init__(self, audio_data: _Optional[bytes] = ..., timestamp: _Optional[int] = ...) -> None: ...

class Transcripts(_message.Message):
    __slots__ = ("transcripts",)
    TRANSCRIPTS_FIELD_NUMBER: _ClassVar[int]
    transcripts: str
    def __init__(self, transcripts: _Optional[str] = ...) -> None: ...
