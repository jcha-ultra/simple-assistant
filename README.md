# Simple LLM Assistant
A lightweight, customizable LLM assistant without a lot of dependencies.

## Features/Characteristics
- Provides a quick and dirty architecture to get started, and also to drop your own logic into without having to learn the intricacies of a whole framework
- Highly customizable: the assistant's prompt, model, knowledge, and memory can all be modularly configured
- Easily swap between different sets of configurations via runtime argument
- Includes 2 example configuration sets

## Installation/Setup
1. Clone this repository.
2. Install the dependencies:
```bash
pip install -r requirements.txt
```
Or use `pyproject.toml` to install with a PEP-518-compliant build tool such as Poetry.
3. The built-in assistant configs use the OpenAI API, so you will need to get one from an OpenAI account.
4. Copy the `.env_template` file and rename it to `.env`. Then, fill in the `OPENAI_API_KEY` value with your API key.
   - If you've already set up the `OPENAI_API_KEY` environment variable on your machine, you can skip this step and just comment this line out.
5. Run the demo to make sure things are working. This will send a test message to the default assistant in a demo conversation:
```bash
python main.py --conv demo
```
6. If the demo ran successfully, you should see a printout of a path that the reply (and the whole conversation) was saved to. You can open this conversation file to see the conversation history.

## Using the Assistant
You can send a message to the assistant by adding it to the end of a conversation file, then running `main.py` with the `--conv` argument set to the conversation file's name. For example, in the demo above, the conversation file was in `conversations/demo.yml`. You can try this out yourself by opening that file and adding a message to the end of it, then running the command from the demo again; the assistant's reply will be written to the end of the file.

A few other notes to keep in mind:
- For convenience, you can also run `python main.py` without any arguments, and by default the `conversations/default.yml` conversation file will be used.
- To get a reply from the assistant, the last message in the conversation file must be from the user, in a valid yml list item format, for example `- user: Hello!`. If the last message isn't from `user`, there will be an error when you run `main.py`.
- The default assistant does not have token management of its inputs, so if your conversation log gets too long you'll have to delete messages from the file to make room in the context. You can add token management via a custom memory module, detailed below.

## Configuration Files
The assistant is highly modular, and can be configured to use different prompts, model APIs, knowledge sources, and memory processing. These module configurations can be bundled into a configuration set defined in files in the `configs` directory. A specific configuration set can be used at runtime via the `--config` argument, i.e. `python main.py --config config_file`.

2 example configuration sets are included:
- `default`: uses `gpt-3.5-turbo` with a simple assistant prompt. Close to the default behavior for most instruction-tuned LLMs.
- `mordin`: uses `gpt-4` and has a prompt that emulates speech patterns of Mordin Solus from Mass Effect—adapted from the [prompt by @daveshap](https://github.com/daveshap/Mordin_Solus_Mode). Should help with reducing token counts and orient replies toward a more concise, technical style.

If a `--config` argument is not specified at runtime, then the `default` configuration will be used.

## Customizing Configurations
You can create your own configuration files; the easiest way to do so is to copy one of the existing ones and modify it. The configuration files define what modules that the assistant uses for its various components.

The components are the following:
- Prompts: defines the prompts that shape the assistant's behavior.
- Model API: the API for the LLM that the assistant uses to generate its replies. Contains functionality for converting the assistant's prompt and conversation history into a format that the API can understand, and for processing the API's response into a reply.
- Knowledge: what background knowledge the assistant is given; can be used to programmatically provide information to the assistant that is not in its training data.
- Memory: how the assistant processes its conversation history; can be used to manage context length or change the conversation text. The output for this module is the conversation history that is passed to the model API.

The repository doesn't include much built-in code for the assistant modules, but the included modules referenced by the example configurations should serve as templates for creating your own.
