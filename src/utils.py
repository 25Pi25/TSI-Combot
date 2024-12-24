import math

from discord import User, Member

from src.constants import ADMIN_ID
from tsi_types import Character


def title_case(string: str) -> str:
    return string[0].upper() + string[1:].lower()


def is_admin(user: User | Member) -> bool:
    return str(user.id) == ADMIN_ID


def score_to_mod(score: int, has_tag: bool = False):
    tag_bonus = 1 if has_tag else 0
    return math.floor((score + tag_bonus - 10) / 2)


def mod_to_string(mod: int):
    if mod == 0:
        return ""
    if mod > 0:
        return f"+{str(mod)}"
    return str(mod)


def calc_initiative_roll(character: Character):
    return f'1d20{mod_to_string(score_to_mod(character.dex_score))}'
