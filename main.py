import json
from dataclasses import dataclass

import discord
from discord import app_commands
from typing import Optional
from random import randint


# CLIENT-SIDE CODE IS HERE
@dataclass
class Character:
    name: str
    level: int
    type1: str
    type2: str
    players: []
    moves: []
    traits: []


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
with open('typechart.csv', 'r') as file:
    typechart_rows = file.readlines()
    file.close()
types = typechart_rows.pop(0).lower().split(",")
types.pop(0)
types.pop()
for row in typechart_rows:
    typechart_row = []
    for value in row.split(","):
        if value in ["", "0", "1/2", "2", "4"]:
            typechart_row.append(value)
    typechart.append(typechart_row)
print(types)
print(typechart)


# ALL THE DISCORD CODE GOES BELOW
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
    if output < 0:  # cannot go weaker than double resist unless one of the types is an immunity (which is already accounted for); round up if it is.
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


# Open the secrets.json file and load the data
with open('secrets.json', 'r') as file:
    data = json.load(file)
    file.close()

# Access the 'token' value
TOKEN = data.get('token')
GUILD = data.get('guild')

myIntents = discord.Intents.all()
MY_GUILD = discord.Object(id=GUILD)  # replace with your guild id


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


client = MyClient(intents=myIntents)


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


@client.tree.command()
async def roll(interaction: discord.Interaction, throws: int, sides: int):
    """Rolls dice."""
    i = 0
    results = []
    while i != throws:
        results.append(randint(1, sides))
        i += 1
    dice_sum = 0
    for rolls in results:
        dice_sum += rolls
    await interaction.response.send_message(f"{throws}d{sides} resulted in {results} for a sum of {dice_sum}")


client.run(TOKEN)
