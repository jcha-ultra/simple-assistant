"""Implementation for chat models from OpenAI."""

import os
from typing import Any, Dict
import openai
from simple_assistant.types import Message, MessageSequence


def get_max_tokens(model_name: str) -> int:
    """Get the maximum number of tokens for the model."""

    max_token_mapping = {
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
    }
    try:
        max_tokens = max_token_mapping[model_name]
    except KeyError as error:
        raise ValueError(f"Model name {model_name} not found.") from error
    return max_tokens


def run(
    messages: MessageSequence,
    model_name: str,
    model_args: Dict[str, Any],
    environment: Dict[str, Any],
) -> str:
    """Run the chat models from OpenAI."""

    def process_message(message: Message) -> Dict[str, Any]:
        """Convert a message into format for OpenAI API."""
        return {"role": message.type, "content": message.content}

    environment = {**os.environ, **environment}

    processed_messages = [process_message(message) for message in messages]
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=processed_messages,
        **model_args,
        api_key=environment["OPENAI_API_KEY"]
        # model=model_name, messages=[{"role": "user", "content": "Hello!"}], **settings
    )
    return response.choices[0]["message"]["content"]
