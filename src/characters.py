import json
from json import JSONDecodeError
from os import path

from src.constants import CHARACTERS_DIR
from src.tsi_types import Character


def load_character_json(name: str) -> object:
    json_path = path.join(CHARACTERS_DIR, f"{name.lower()}.json")
    if not path.exists(json_path):
        raise LookupError(f"Character {name} could not be found in the specified character list.")
    with open(json_path, 'r') as json_text:
        try:
            return json.load(json_text)
        except JSONDecodeError as e:
            raise JSONDecodeError(f"JSON for {name} is invalid. Details: {e.args}", e.doc, e.pos)


def load_character(name: str) -> Character:
    char_json = load_character_json(name)
    return Character.model_validate(char_json)


def save_character(char: Character):
    json_path = path.join(CHARACTERS_DIR, f"{char.name.lower()}.json")
    with open(json_path, 'w') as file:
        file.write(str(char.model_dump_json()))


def create_character(json_data: object) -> Character:
    return Character.model_validate(json_data)
