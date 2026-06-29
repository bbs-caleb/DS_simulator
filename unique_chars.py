import json
from typing import List


def unique_chars(json_path: str) -> List[str]:
    with open(json_path, "r", encoding="utf-8") as file:
        messages = json.load(file)

    unique_characters = set()

    for message_data in messages:
        message_text = message_data["message"]
        unique_characters.update(message_text)

    return list(unique_characters)
