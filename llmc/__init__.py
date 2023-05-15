system_message = """
You are a compiler. With each input from the user, you output a json object with three keys:
1. The current state which represents any persistent memory or variables and
2. Any output from the previous instructions.
3. A list of commands, if necessary, to interact with the filesystem.

Valid commands are:
    Read a file: ["read", "filename"]
    Write a file: ["write", "filename", "content"]
    Request input from the user: ["input", "message for user"]
    List files in a directory: ["list", "path"]

Return only the json object.

Example:
save the value 4 into x and the value hello into z.
```json
{
    "state": {
        "x": 4,
        "z": "hello",
    },
    "output": "",
    "command": []
}
```

What is the value of z without any vowels?
```json
{
    "state": {
        "x": 4,
        "z": "hello",
    },
    "output": "hll",
    "command": []
}
```

Create a file named temp.txt with the value of z written x times.
```json
{
    "state": {
        "x": 4,
        "z": "hello",
    },
    "output": "",
    "command": ["write", "temp.txt", "hello\nhello\nhello\nhello"]
}
```

Example:
Read the temp.json file into memory.
```json
{
    "state": {},
    "output": "",
    "command": ["read", "temp.json"]
}
```

Here are the contents of temp.json:
{
    "example": "text content",
    "key_2": 2
}
```json
{
    "state": {
        "temp.json_content": {
            "example": "text content",
            "key_2": 2
        }
    },
    "output": "",
    "command": []
}
```
"""

import json
import logging
import os
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

messages = [{"role": "system", "content": system_message}]

def compile(text: str) -> tuple[str, str]:
    logger.info(f"Compiling: {text}")
    messages.append({"role": "user", "content": text})
    response = openai.ChatCompletion.create(messages=messages, model="gpt-4")
    messages.append(response.choices[0].message)
    logger.info(f"Response: {response.choices[0].message}")
    data = json.loads(response.choices[0].message.content)
    return data.get("state"), data.get("output"), data.get("command")

def handle_read(command):
    if os.path.exists(command[1]):
        with open(command[1]) as f:
            content = f.read()
            return compile(f"Here is the content of {command[1]}:\n{content}")
    else:
        raise FileNotFoundError()

def handle_write(command):
    with open(command[1], "w") as f:
        f.write(command[2])

def handle_input(command):
    content = input(command[1])
    return compile(f"Here is the user input:\n{content}")

def handle_list(command):
    content = os.listdir(command[1])
    return compile(f"Here is the list of files in that directory:\n{content}")


# Allow cli
def main():
    state, output, command = {}, "", []
    while True:
        line = input("> ")
        if line == "q" or line == "quit":
            break

        if line == "state":
            print(state)
            continue

        if line == "output":
            print(output)
            continue
        
        if line == "command":
            print(command)
            continue

        state, output, command = compile(line)
        count = 0
        while command:
            if command[0] == "read":
                state, output, command = handle_read(command)
            elif command[0] == "input":
                state, output, command = handle_input(command)
            elif command[0] == "list":
                state, output, command = handle_list(command)
            elif command[0] == "write":
                handle_write(command)
                command = []
            count += 1
            # Don't let this go too crazy
            if count > 3:
                break

        print(output)

__all__ = ["main"]

