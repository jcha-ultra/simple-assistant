"""Runs the assistant."""

from argparse import ArgumentParser, Namespace
import sys

sys.path.append("")

from simple_assistant.core import run_assistant

DEFAULT_CONFIG = "default"
DEFAULT_CONVERSATION = "default"


def get_args() -> Namespace:
    """Get the command line arguments."""

    parser = ArgumentParser()
    parser.add_argument(
        "--config",
        dest="config_file",
        help="The location of the configuration file.",
        metavar="CONFIG_LOCATION",
    )
    parser.add_argument(
        "--conv",
        dest="conversation",
        help="The conversation thread to run.",
        metavar="CONVERSATION_THREAD",
    )
    args = parser.parse_args()
    return args


def main():
    """Run the assistant."""
    args = get_args()
    if args.config_file is None:
        args.config_file = DEFAULT_CONFIG
    if args.conversation is None:
        args.conversation = DEFAULT_CONVERSATION
    run_assistant(args.config_file, args.conversation, write_conversation=True)


if __name__ == "__main__":
    main()
