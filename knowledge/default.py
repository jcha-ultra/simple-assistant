"""Default knowledge module."""

from typing import Optional

from simple_assistant.types import MessageSequence


def load_knowledge(
    conversation_history: MessageSequence, user_input: str
) -> Optional[str]:
    """Load the knowledge that the assistant has."""
    return None
