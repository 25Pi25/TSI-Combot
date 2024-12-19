import json
from dataclasses import dataclass
from json import JSONDecodeError
from math import floor
from os import walk

import discord
from discord import app_commands
from typing import Optional
from random import randint

# CONSTANTS
with open('secrets.json', 'r') as file:
    secrets = json.load(file)
CHARACTERS_DIR = './characters'
TOKEN = secrets.get('token')
GUILD_ID = secrets.get('guild')
ADMIN_ID = secrets.get('admin')

BOT_INTENTS = discord.Intents.all()
MY_GUILD = discord.Object(id=GUILD_ID)


# CLIENT-SIDE CODE IS HERE
@dataclass
class Character:
    name: str
    filename: str
    level: int
    type1: str
    type2: str
    players: []
    str_score: int
    dex_score: int
    con_score: int
    int_score: int
    wis_score: int
    cha_score: int
    spe_score: int
    moves: []
    traits: []
    initiative_pending: bool
    initiative: int


@dataclass
class Move:
    move_name: str
    move_type: str
    base_damage_rolls: int
    base_damage_sides: int
    base_accuracy_mod: int
    base_heal_rolls: int
    base_heal_sides: int
    tactics: str


typechart = []
with open('typechart.csv', 'r') as typechart_csv:
    typechart_rows = typechart_csv.readlines()
types = typechart_rows.pop(0).lower().split(",")
types.pop(0)
types.pop()
for row in typechart_rows:
    typechart_row = []
    for value in row.split(","):
        if value in ["", "0", "1/2", "2", "4"]:
            typechart_row.append(value)
    typechart.append(typechart_row)


# TYPE CALCULATION CODE


def type_matchup_calc(attacking_type, defending_type_1, defending_type_2=-1, type_ring=-1, barrier=False, breaker=False,
                      sheer_force=False):
    attacker_to_defender_1 = single_type_calc(attacking_type, defending_type_1, False, barrier, breaker,
                                              sheer_force)  # no need to run a check for the first type; it's not allowed to be blank
    if defending_type_2 == -1:  # if second type is blank, ignore it (treat as neutrality.)
        attacker_to_defender_2 = 3
    else:
        attacker_to_defender_2 = single_type_calc(attacking_type, defending_type_2, False, barrier,
                                                  breaker, sheer_force)
    if type_ring == -1:  # if type ring is blank, ignore it (treat as neutrality.)
        attacker_to_type_ring = 3
    else:
        attacker_to_type_ring = single_type_calc(attacking_type, type_ring, True, barrier, breaker,
                                                 sheer_force)
    # Matchup sums.
    if attacker_to_defender_1 == 0 or attacker_to_defender_2 == 0 or attacker_to_type_ring == 0:  # Immunities cannot be overridden (sheer force has already been accounted for here, so if there is one, the matchup is an immunity.)
        return 0
    output = attacker_to_defender_1 + attacker_to_defender_2 + attacker_to_type_ring - 6  # okay, the math on this one is wonky! we want to treat neutrality as 0, so it'll do nothing. we need to subtract each relation by 3, since that's what they have for neutrality. there's 3 relations, -3*3=-9. of course, we want to shift it back at the end, so we add 3 back. -9+3=-6
    if output > 5:  # cannot go stronger than double weakness; round down if it is.
        output = 5
    if output <= 0:  # cannot go weaker than double resist unless one of the types is an immunity (which is already accounted for); round up if it is.
        output = 1
    return output


def single_type_calc(attacking_type, defending_type, is_type_ring, barrier, breaker, sheer_force):
    # ATTACKER: column. DEFENDER: row. typechart[row][column]
    # OUTPUTS: 0 = immune, 1 = double resist, 2 = resist, 3 = neutral, 4 = weak, 5 = double weak
    spreadsheet_values = ["0", "1/4", "1/2", "", "2", "4"]
    if defending_type == "":
        return -1
    else:
        output = spreadsheet_values.index(typechart[attacking_type][
                                              defending_type])  # I have literally no clue why it isn't the other way around, but I was getting a flipped typechart.
        if is_type_ring and output >= 4:  # Type rings should not apply weaknesses; treat as neutral.
            output = 3
        if barrier and output <= 2:  # Barrier converts immunity/resistance/double-resistance into immunity.
            output = 0
        if breaker and output <= 2:  # Breaker converts immunity/resistance/double-resistance into neutrality. This will override Barrier if both are applied.
            output = 3
        if sheer_force and output == 0:  # Sheer Force converts immunity into neutrality.
            output = 3
        return output


def type_name_to_index(name):
    if name == "":
        return -1
    try:
        return types.index(name.lower())
    except ValueError:
        return -2


def type_calc_words(attacking_type, defending_type_1, defending_type_2="", type_ring="", barrier=False, breaker=False,
                    sheer_force=False):
    attacking_type_index = type_name_to_index(attacking_type)
    defending_type_1_index = type_name_to_index(defending_type_1)
    defending_type_2_index = type_name_to_index(defending_type_2)
    type_ring_index = type_name_to_index(type_ring)
    if defending_type_1_index == defending_type_2_index:
        return "Defending types cannot be the same."
    if attacking_type_index == -1 or defending_type_1_index == -1:  # attacking type and first defending type are not allowed to be blank; return error if it is.
        return "Attacking type / first defending type cannot be blank."
    if attacking_type_index == -2 or defending_type_1_index == -2 or defending_type_2_index == -2 or type_ring_index == -2:  # if any types are invalid, return error.
        return "Input contains an invalid type name."
    number = type_matchup_calc(attacking_type_index, defending_type_1_index, defending_type_2_index, type_ring_index,
                               barrier, breaker,
                               sheer_force)
    words = ["is immune to", "double-resists", "resists", "is neutral to", "is weak to", "is double weak to"]
    relation = words[number]

    defender_name = title_case(defending_type_1)
    if defending_type_2 != "":
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
    return f"{defender_name} {relation} {attacker_name}."


def title_case(input_val):
    string_list = list(input_val)
    output = string_list.pop(0).upper()
    for letter in string_list:
        output += letter.lower()
    return output


# COMBAT STATES: 0 = not in combat, 1 = initiative pending
combat_state = 0


# CHARACTER LOADING


def json_data_by_char_name(name: str):
    all_files = next(walk(CHARACTERS_DIR), (None, None, []))[2]  # [] if no file
    # convert all_files to lowercase
    all_files_lower = []
    for filename in all_files:
        all_files_lower.append(filename.lower())
    if f'{name.lower()}.json' in all_files_lower:
        with open(f'{CHARACTERS_DIR}/' + all_files[all_files_lower.index(f'{name.lower()}.json')], 'r') as char_file:
            try:
                char_json_data = json.load(char_file)
            except JSONDecodeError as e:
                raise JSONDecodeError(f"JSON for {name} is invalid. Details: {e.args}", e.doc, e.pos)
        return char_json_data
    else:
        raise LookupError(f"JSON for character {name} could not be found.")


def load_character_from_json_data(json_data, filename: str):  # going to be coming back to this one a lot lmao
    # JSON VALIDITY CHECKS SHOULD BE HAPPENING IN THIS FUNCTION
    char = Character
    char.name = json_data.get('name')
    char.filename = filename.lower()
    char.str_score = json_data.get('str_score')
    char.dex_score = json_data.get('dex_score')
    char.con_score = json_data.get('con_score')
    char.int_score = json_data.get('int_score')
    char.wis_score = json_data.get('wis_score')
    char.cha_score = json_data.get('cha_score')
    char.spe_score = json_data.get('spe_score')
    return char


def character_string_to_list(characters: str):
    character_string_list = characters.split(",")
    character_name_list = []
    for character_name in character_string_list:
        character_name_list.append(character_name.replace(" ", ""))
    return character_name_list


def load_characters_from_string(characters: str):
    character_name_list = character_string_to_list(characters)
    chars = []
    for character_name in character_name_list:
        chars.append(load_character_from_json_by_name(character_name))
    return chars


def load_character_from_json_by_name(character: str):
    return load_character_from_json_data(json_data_by_char_name(character), character)


def character_index_from_list_by_name(name: str, character_list: []):
    for character in character_list:
        if character.filename == name.lower():
            return character_list.index(character)
    raise LookupError(f"Character {name} could not be found in the specified character list.")


# STAT CALCULATIONS
def score_to_mod(score: int, has_tag: bool = False):
    tag_bonus = 0
    if has_tag:
        tag_bonus = 1
    return floor((score + tag_bonus - 10) / 2)


def mod_as_string(mod: int):
    if mod == 0:
        return ""
    if mod > 0:
        return f"+{str(mod)}"
    else:
        return str(mod)


def calc_initiative_roll(character: Character):
    return f'1d20{mod_as_string(score_to_mod(character.dex_score))}'


combat_characters = []


def try_start_combat(characters: str):
    try:
        global combat_characters
        global combat_state
        combat_characters = load_characters_from_string(characters)
        for combat_character in combat_characters:
            combat_character.initiative_pending = True
        combat_state = 1
    except Exception as e:
        return e.args


initiative_lobby_new_message = ""
trigger_initiative_lobby_update = False


def update_initiative_lobby(characters: []):
    output = "```\nROLL INITIATIVE!\n"
    for character in characters:
        initiative_indicator = ""
        if not character.initiative_pending:
            initiative_indicator = "(!) "
        output += f'{initiative_indicator}{character.name}: {calc_initiative_roll(character)}\n'
    output += "Use /set_initiative once you've rolled!\n```"
    global initiative_lobby_new_message
    global trigger_initiative_lobby_update
    initiative_lobby_new_message = output
    trigger_initiative_lobby_update = True


def set_char_initiative(char_name: str, initiative_value: int):
    global combat_characters
    index = character_index_from_list_by_name(char_name, combat_characters)
    combat_characters[index].initiative = initiative_value
    combat_characters[index].initiative_pending = False
    update_initiative_lobby(combat_characters)


def start_combat():
    return None


# ALL THE DISCORD CODE GOES BELOW


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


client = MyClient(intents=BOT_INTENTS)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')


@client.tree.command()
async def type_matchup(interaction: discord.Interaction, attacking_type: str, defending_type_1: str,
                       defending_type_2: Optional[str] = "", type_ring: Optional[str] = "",
                       barrier: Optional[bool] = False,
                       breaker: Optional[bool] = False, sheer_force: Optional[bool] = False):
    """Returns a type matchup."""
    await interaction.response.send_message(
        type_calc_words(attacking_type, defending_type_1, defending_type_2, type_ring, barrier, breaker, sheer_force))


extra_output_text = "d resulted in[]for a sum of"


def dice_roll(throws: int, sides: int):
    i = 0
    results = []
    if throws <= 0:
        return "Throws must be positive."
    if sides < 1:
        return "Sides must be 1 or more."
    if len((str(sides) + ", ") * throws) + len(str(sides * throws)) + len(extra_output_text) > 2000:
        return "Too big!"
    while i != throws:
        results.append(randint(1, sides))
        i += 1
    dice_sum = 0
    for rolls in results:
        dice_sum += rolls
    return f"{throws}d{sides} resulted in {results} for a sum of {dice_sum}"


@client.tree.command()
async def roll(interaction: discord.Interaction, throws: int, sides: int):
    """Rolls dice."""
    print(f'{interaction.user.display_name} rolled {throws}d{sides}')
    await interaction.response.send_message(dice_roll(throws, sides))


@client.tree.command()
async def set_initiative(interaction: discord.Interaction, character_name: str, initiative: int):
    set_char_initiative(character_name, initiative)
    await interaction.response.send_message("Initiative set! (this message will be private when i figure out how)")


@client.tree.command()
async def start_combat(interaction: discord.Interaction, characters: str):
    if interaction.user.id != ADMIN_ID:
        await interaction.response.send_message("You are not an admin!")
    else:
        global trigger_initiative_lobby_update
        global initiative_lobby_new_message
        global combat_characters
        global combat_state
        try_start_combat_output = try_start_combat(characters)
        if try_start_combat_output is not None:
            await interaction.response.send_message(try_start_combat_output)
        else:
            await interaction.response.send_message("Combat started!")
            update_initiative_lobby(combat_characters)
            while combat_state == 1:
                if trigger_initiative_lobby_update:
                    trigger_initiative_lobby_update = False
                    await interaction.edit_original_response(content=initiative_lobby_new_message)

client.run(TOKEN)
