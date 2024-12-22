from discord import Interaction

from src.constants import client, ADMIN_ID
from src.characters import character_index_from_list_by_name, load_characters_from_string
from src.utils import calc_initiative_roll

combat_state = 0
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


@client.tree.command()
async def set_initiative(interaction: Interaction, character_name: str, initiative: int):
    set_char_initiative(character_name, initiative)
    await interaction.response.send_message("Initiative set!", ephemeral=True)


@client.tree.command()
async def start_combat(interaction: Interaction, characters: str):
    if str(interaction.user.id) != ADMIN_ID:
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
