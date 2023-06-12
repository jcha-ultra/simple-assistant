from typing import Literal, Mapping, Sequence

MessageType = Literal["user", "assistant", "system"]
MessageSequence = Sequence[Mapping[MessageType, str]]
