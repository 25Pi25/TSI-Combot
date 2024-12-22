from typing import Optional

from discord import Interaction

from src.constants import typechart, client
from src.tsi_types import Type
from src.utils import title_case


def get_type_multiplier(attacking_type: Type, defending_type: Type, is_type_ring=False, barrier=False, breaker=False,
                        sheer_force=False) -> float:
    raw_mult = typechart[attacking_type][defending_type]
    if is_type_ring:  # Type rings should not apply weaknesses; treat as neutral.
        raw_mult = min(raw_mult, 1)
    if barrier and raw_mult < 1:  # Barrier converts immunity/resistance/double-resistance into immunity.
        raw_mult = 0
    if breaker and raw_mult < 1:  # Breaker converts immunity/resistance/double-resistance into neutrality. This will override Barrier if both are applied.
        raw_mult = 1
    if sheer_force and raw_mult == 0:  # Sheer Force converts immunity into neutrality.
        raw_mult = 1
    return raw_mult


def get_multiplier_description(multiplier: float) -> str:
    return {
        0: "is immune to",
        0.25: "double-resists",
        0.5: "resists",
        1: "is neutral to",
        2: "is weak to",
        4: "is double weak to"
    }[multiplier]


def get_matchup_description(attacking_type: Type, defending_type_1: Type, defending_type_2: Optional[Type] = None,
                            type_ring: Optional[Type] = None,
                            barrier=False, breaker=False,
                            sheer_force=False):
    if defending_type_1 is defending_type_2:
        return "Defending types cannot be the same."
    # TODO: call type_matchup_calc when you actually do this (actually i dunno if i even need the function)
    multiplier = get_type_multiplier(attacking_type, defending_type_1,
                                     type_ring is not None and type_ring is defending_type_1, barrier, breaker,
                                     sheer_force)
    if defending_type_2:
        multiplier *= get_type_multiplier(attacking_type, defending_type_2,
                                          type_ring is not None and type_ring is defending_type_2,
                                          barrier, breaker, sheer_force)
    description = get_multiplier_description(multiplier)

    defender_name = title_case(defending_type_1)
    if defending_type_2:
        defender_name += f"/{title_case(defending_type_2)}"

    defender_clauses = 0
    if type_ring != "":
        defender_clauses += 0b1
    if barrier:
        defender_clauses += 0b10
    if breaker:
        defender_clauses += 0b100
    match defender_clauses:
        case 0b0:
            defender_name += ""
        case 0b1:
            defender_name += f" ({title_case(type_ring)} ring)"
        case 0b10:
            defender_name += " (with Barrier)"
        case 0b11:
            defender_name += f" ({title_case(type_ring)} ring, with Barrier)"
        case 0b100:
            defender_name += " (with Breaker)"
        case 0b101:
            defender_name += f" ({title_case(type_ring)} ring, with Breaker)"
        case 0b110:
            defender_name += " (with Barrier and Breaker)"
        case 0b111:
            defender_name += f" ({title_case(type_ring)} ring, with Barrier and Breaker)"

    attacker_name = title_case(attacking_type)
    if sheer_force:
        attacker_name += " (with Sheer Force)"
    return f"{defender_name} {description} {attacker_name}."


@client.tree.command()
async def type_matchup(interaction: Interaction, attacking_type: str, defending_type_1: str,
                       defending_type_2: Optional[str] = "", type_ring: Optional[str] = "",
                       barrier: Optional[bool] = False,
                       breaker: Optional[bool] = False, sheer_force: Optional[bool] = False):
    """Returns a type matchup."""
    await interaction.response.send_message(
        get_matchup_description(Type(attacking_type), Type(defending_type_1),
                                defending_type_2 and Type(defending_type_2),
                                type_ring, barrier, breaker, sheer_force))
