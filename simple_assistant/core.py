"""Core module for the simple assistant."""

from pathlib import Path
from typing import Optional

from yaml import safe_load

from .utilities import quick_import
from .types import MessageSequence


def run_assistant(conversation: str, user_input: Optional[str] = None):
    """Run the assistant."""
    with open("config.yml", encoding="utf-8") as config_file:
        config = safe_load(config_file)
    prompts: MessageSequence = quick_import(Path(f"prompts/{config['prompt']}.py")).load_prompts()
    conversation_path = Path(f"conversations/{conversation}.yml")
    if not conversation_path.exists():
        conversation_path.touch()
        conversation_path.write_text("[]", encoding="utf-8")
    with open(
        f"conversations/{conversation}.yml", encoding="utf-8"
    ) as conversation_file:
        conversation_history: MessageSequence = safe_load(conversation_file)
    # if user input was not provided, use the input from the last message
    if user_input is None:
        try:
            user_input = conversation_history[-1]["user"]
        except (IndexError, KeyError) as error:
            raise ValueError(
                "No user input provided and no user input found in conversation file."
            ) from error
        conversation_history = conversation_history[:-1]
    # if user input was provided, and input also exists in conversation history, then there's a conflict
    elif conversation_history and "user" in conversation_history[-1]:
        raise ValueError(
            "User input provided, but user input already exists in conversation file."
        )

    knowledge: Optional[str] = quick_import(
        Path(f"knowledge/{config['knowledge']}.py")
    ).load_knowledge(conversation_history, user_input)
    
    memory: Optional[MessageSequence] = quick_import(
        Path(f"memory/{config['memory']}.py")
    ).load_memory(knowledge, conversation_history, user_input)

    messages = [
        {"system": knowledge} if knowledge is not None else None,
        *memory,
        *prompts,
        {"user": user_input},
    ]
    messages = [message for message in messages if message is not None]

    breakpoint()
    model = quick_import(Path(f"models/{config['model']}.py")).load_model()

    response = model.run(messages)
    conversation_history = [*conversation_history, {"user": user_input}, {"assistant": response}]
    from yaml import safe_dump
    with open(
        f"conversations/{conversation}.yml", mode="w", encoding="utf-8"
    ) as conversation_file:
        safe_dump(conversation_history, conversation_file, default_flow_style=False, allow_unicode=True)
    breakpoint()
