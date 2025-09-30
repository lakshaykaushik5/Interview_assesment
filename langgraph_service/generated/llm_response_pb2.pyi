from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class InputTranscripts(_message.Message):
    __slots__ = ("input_transcripts",)
    INPUT_TRANSCRIPTS_FIELD_NUMBER: _ClassVar[int]
    input_transcripts: str
    def __init__(self, input_transcripts: _Optional[str] = ...) -> None: ...

class OutputResponse(_message.Message):
    __slots__ = ("output_response",)
    OUTPUT_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    output_response: str
    def __init__(self, output_response: _Optional[str] = ...) -> None: ...
