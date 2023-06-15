"""Type definitions for the assistant."""

from typing import Literal, NamedTuple, Sequence

MessageType = Literal["user", "assistant", "system"]

class Message(NamedTuple):
    """A message from the user, assistant, or system."""
    type: MessageType
    content: str

MessageSequence = Sequence[Message]
