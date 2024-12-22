import math

from tsi_types import Type, Character


def title_case(string: str) -> str:
    return string[0].upper() + string[1:].lower()


def load_typechart() -> dict[Type, dict[Type, float]]:
    """
    Loads the typechart CSV into a data structure.
    :return: A dictionary of attacking types, to a dictionary of defending types to their multiplier
    """
    result = dict()
    with open('../typechart.csv', 'r') as typechart_csv:
        typechart_rows = typechart_csv.readlines()
    # We want to know the index of every type for the csv ONLY in this instance
    # After that, we never have to keep track of index when dealing with the typechart
    # Additionally we are casting str to Type because we know the typechart
    type_row: list[Type] = [Type(cell) for cell in typechart_rows[0].strip().split(",")[1:]]
    for row in typechart_rows[1:]:
        type_matchups: dict[Type, float] = dict()
        this_type, *matchup_values = row.strip().split(",")
        # Skipping the first item because it's the attacker, and zipping to keep track of the defending type
        for defender_type, value in zip(type_row, matchup_values):
            # "or 1" acts as a default value when the string is empty
            type_matchups[defender_type] = float(value or 1)
        result[this_type] = type_matchups
    return result


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
