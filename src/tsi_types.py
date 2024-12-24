from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel


# TODO: having a general type file will be worse when these objects gain their own methods and attributes, so they may
#  have to be relocated into separate files

# Pokémon types, represented by an enum. To convert a str to enum, get by using Type(str)
class Type(str, Enum):
    NORMAL = "Normal",
    FIRE = "Fire",
    WATER = "Water",
    GRASS = "Grass",
    ELECTRIC = "Electric",
    ICE = "Ice",
    FIGHTING = "Fighting",
    POISON = "Poison",
    GROUND = "Ground",
    FLYING = "Flying",
    PSYCHIC = "Psychic",
    BUG = "Bug",
    ROCK = "Rock",
    GHOST = "Ghost",
    DRAGON = "Dragon",
    DARK = "Dark",
    STEEL = "Steel",
    FAIRY = "Fairy",
    COSMIC = "Cosmic",
    SHADOW = "Shadow",
    STELLAR = "Stellar"


# This is a surprise tool that can help us later
class Tactic(str, Enum):
    BOLSTER = "Bolster"
    UNDERMINE = "Undermine"
    EMPOWER = "Empower"
    ENFEEBLE = "Enfeeble"
    FOCUSING = "Focusing"
    DISTRACTING = "Distracting"
    SWIFTENING = "Swiftening"
    SLOWING = "Slowing"
    EXHAUSTING = "Exhausting"
    MUSCLE_MEMORY = "Muscle Memory"
    RELIEVE = "Relieve"
    SNIPER = "Sniper"
    MARKSMAN = "Marksman"
    TAUNT = "Taunt"
    BESTOW_PARALYSIS = "Bestow Status (Paralysis)"
    BESTOW_BURNING = "Bestow Status (Burning)"
    BESTOW_CONFUSION = "Bestow Status (Confusion)"
    BESTOW_POISON = "Bestow Status (Poison)"
    BESTOW_FLINCHING = "Bestow Status (Flinching)"
    BESTOW_FROZEN = "Bestow Status (Frozen)"
    BESTOW_TRAPPING = "Bestow Status (Trapping)"
    TANTRUM = "Tantrum"
    PICKPOCKET = "Pickpocket"
    BURST = "Burst"
    STATUS_BURST = "Status Burst"
    SHEER_FORCE = "Sheer Force"
    PAY_DAY = "Pay Day"
    PLAY_DIRTY = "Play Dirty"
    FICKLE = "Fickle"
    DISABLE = "Disable"
    STAKEOUT = "Stakeout"
    STUDY = "Study"
    CHOICED = "Choiced"
    DEEP_WOUNDS = "Deep Wounds"
    PROTECT = "Protect"
    TYPE_EXPERT = "Type Expert"
    STATUS_EXPERT = "Status Expert"
    STORED_POWER = "Stored Power"
    FACADE = "Facade"
    INERTIA = "Inertia"
    MULTI_HIT = "Multi-Hit"
    BEAT_UP = "Beat Up"
    BATON_PASS = "Baton Pass"
    SNATCH = "Snatch"
    DESPERATION = "Desperation"
    SYMBIOSIS = "Symbiosis"
    BREAKER = "Breaker"
    BODYGUARD = "Bodyguard"
    BARRIER = "Barrier"
    SHIELD_DUST = "Shield Dust"
    HEAL_BLOCK = "Heal Block"
    CONDITION_BURST = "Condition Burst"
    COUNTER_ATTACK = "Counter Attack"
    SPEED_BOOST = "Speed Boost"


@dataclass
class Move:
    move_name: str
    move_type: str
    base_damage_rolls: int
    base_damage_sides: int
    base_accuracy_mod: int
    base_heal_rolls: int
    base_heal_sides: int
    tactics: list[Tactic]


@dataclass
class Character(BaseModel):
    name: str
    level: int
    type1: Type
    type2: Type | None
    players: list[str]
    str_score: int
    dex_score: int
    con_score: int
    int_score: int
    wis_score: int
    cha_score: int
    spe_score: int
    moves: list[Move]
    # TODO: add functionality to this maybe idk
    traits: list[str]

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
