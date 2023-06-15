"""Core module for the simple assistant."""

from pathlib import Path
from typing import Optional

from yaml import dump, safe_load

from .utilities import quick_import
from .types import Message, MessageSequence


def run_assistant(conversation: str, user_input: Optional[str] = None):
    """Run the assistant."""
    with open("config.yml", encoding="utf-8") as config_file:
        config = safe_load(config_file)
    prompts: MessageSequence = quick_import(
        Path(f"prompts/{config['prompt']}.py")
    ).load_prompts()
    conversation_path = Path(f"conversations/{conversation}.yml")
    if not conversation_path.exists():
        conversation_path.touch()
        conversation_path.write_text("[]", encoding="utf-8")
    with open(
        f"conversations/{conversation}.yml", encoding="utf-8"
    ) as conversation_file:
        conversation_history: MessageSequence = [
            Message(*next(iter(message.items())))
            for message in safe_load(conversation_file)
        ]
    # if user input was not provided, use the input from the last message
    if user_input is None:
        if not conversation_history or conversation_history[-1].type != "user":
            raise ValueError(
                "No user input provided and no user input found in conversation file."
            )
        user_input = conversation_history[-1].content
        conversation_history = conversation_history[:-1]
    # if user input was provided, and input also exists in conversation history, then there's a conflict
    elif conversation_history and conversation_history[-1].type == "user": 
        raise ValueError(
            "User input provided, but user input already exists in conversation file."
        )
    model = quick_import(Path(f"model_apis/{config['model_api']}.py"))
    max_tokens: int = model.get_max_tokens(config["model_name"])

    knowledge: Optional[str] = quick_import(
        Path(f"knowledge/{config['knowledge']}.py")
    ).load_knowledge(conversation_history, user_input)

    memory: MessageSequence = quick_import(
        Path(f"memory/{config['memory']}.py")
    ).load_memory(knowledge, conversation_history, user_input, max_tokens)
    messages = [
        Message("system", knowledge) if knowledge is not None else None,
        *memory,
        *prompts,
        Message("user", user_input),
    ]
    messages = [message for message in messages if message is not None]
    response: str = model.run(messages, config["model_name"], config["model_settings"])
    conversation_history = [
        *conversation_history,
        Message("user", user_input),
        Message("assistant", response),
    ]
    history_to_save = [
        {message.type: message.content.strip()}
        for message in conversation_history
        if message.type != "system"
    ]

    with open(
        f"conversations/{conversation}.yml", mode="w", encoding="utf-8"
    ) as conversation_file:
        dump(
            history_to_save,
            conversation_file,
            default_flow_style=False,
            default_style="|",
            allow_unicode=True,
            indent=0,
        )
