"""Core module for the simple assistant."""

from functools import reduce
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from yaml import dump, safe_load
from dotenv import dotenv_values

from .utilities import quick_import
from .types import Message, MessageSequence, MessageType


def run_assistant(
    config_file: str,
    conversation: str,
    user_input: Optional[str] = None,
    write_conversation: bool = False,
) -> List[Dict[str, str]]:
    """Run the assistant."""
    with open(Path(f"configs/{config_file}.yml"), encoding="utf-8") as config_file:
        config = safe_load(config_file)
    prompts: MessageSequence = quick_import(
        Path(f"prompts/{config['prompt']}.py")
    ).load_prompts()
    conversation_path = Path(config["conversation_dir"]) / f"{conversation}.yml"
    if not conversation_path.exists():
        conversation_path.touch()
        conversation_path.write_text("[]", encoding="utf-8")
    assistant_name = config["assistant_name"]

    def map_from_assistant_name(name: str, content: str) -> Tuple[MessageType, str]:
        if name == assistant_name:
            return "assistant", content
        if name == "user":
            return "user", content
        raise ValueError(
            f"Unknown name {name} from conversation file. Must be {assistant_name} or user."
        )

    with open(conversation_path, encoding="utf-8") as conversation_file:
        conversation_history: MessageSequence = [
            Message(*map_from_assistant_name(*next(iter(message.items()))))
            for message in safe_load(conversation_file)
        ]
    # if user input was not provided, use the input from the last message
    if user_input is None:
        if not conversation_history or conversation_history[-1].type != "user":
            raise ValueError(
                f'Conversation thread `{conversation_path}` must end with a user message. Please make sure that the last line of the yml file is from the user. Example: "- user: Tell me about yourself.")'
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
    environment_values = reduce(
        lambda dict_1, dict_2: {**dict_1, **dict_2},
        [dotenv_values(Path(env_file)) for env_file in config["environment_variables"]],
    )
    response: str = model.run(
        messages, config["model_name"], config["model_args"], environment_values
    )
    conversation_history = [
        *conversation_history,
        Message("user", user_input),
        Message("assistant", response.replace(" \n", "\n")),
    ]

    def map_to_assistant_name(message_type: MessageType) -> str:
        if message_type == "assistant":
            return assistant_name
        if message_type == "user":
            return message_type
        raise ValueError(
            f"Cannot map message type `{message_type}`. Must be `assistant` or `user`."
        )

    history_to_save = [
        {map_to_assistant_name(message.type): message.content.strip()}
        for message in conversation_history
        if message.type != "system"
    ]
    if write_conversation:
        with open(conversation_path, mode="w", encoding="utf-8") as conversation_file:
            dump(
                history_to_save,
                conversation_file,
                default_flow_style=False,
                default_style="|",
                allow_unicode=True,
                indent=0,
            )
        print(f"Reply saved to \033[32m`{conversation_path.absolute()}`.\033[0m")
    return history_to_save
