import discord.ui
from discord import Interaction

from src.characters import load_character
from src.constants import client, ADMIN_ID
from src.tsi_types import Character
from src.utils import title_case


class InitiativeModal(discord.ui.Modal, title="Set Initiative"):
    def __init__(self, character_names: list[str]):
        super().__init__()
        self.character_names = [name.lower() for name in character_names]

    character_name = discord.ui.TextInput(
        label="Character Name",
        placeholder="Name goes here..."
    )
    initiative = discord.ui.TextInput(
        label="Total Initiative",
        placeholder="Enter a number here..."
    )

    is_valid = False

    async def on_submit(self, interaction: Interaction) -> None:
        # on submit will only validate the modal. the view awaiting a response will handle other logic
        if self.character_name.value.lower() not in self.character_names:
            await interaction.response.send_message("Character does not exist. Try searching again.", ephemeral=True)
            raise Exception()
        if not self.initiative.value.isdigit():
            await interaction.response.send_message("Initiative is not a number. Try again.", ephemeral=True)
            raise Exception()
        self.is_valid = True
        self.stop()
        await interaction.response.send_message(
            f"{self.character_name.value}'s initiative set to {self.initiative.value}.", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        if interaction.response.is_done():
            return
        await interaction.response.send_message(f"Couldn't set initiative. Try again.", ephemeral=True)
        self.stop()


class InitiativeView(discord.ui.view.View):
    is_full = False

    def __init__(self, characters: list[Character]):
        super().__init__()
        self.characters = characters
        self.initiatives: dict[Character, int] = dict()

    @discord.ui.button(label="Set initiative!", style=discord.ButtonStyle.success)
    async def on_success_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = InitiativeModal([char.name for char in self.characters])
        await interaction.response.send_modal(modal)
        await modal.wait()
        if not modal.is_valid:
            return
        target_name = title_case(modal.character_name.value)
        target_char = next(char for char in self.characters if char.name == target_name)
        self.initiatives[target_char] = int(modal.initiative.value)
        if len(self.initiatives) == len(self.characters):
            self.is_full = True
            self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def on_danger_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != ADMIN_ID:
            await interaction.response.send_message("You are not an admin!", ephemeral=True)
            return
        await interaction.response.send_message("Cancelling battle...", ephemeral=True)
        self.stop()



@client.tree.command()
async def start_combat(interaction: Interaction, characters: str):
    if str(interaction.user.id) != ADMIN_ID:
        await interaction.response.send_message("You are not an admin!", ephemeral=True)
        return
    # TODO: prevent duplicates from being listed
    character_list = [load_character(name.strip()) for name in characters.split(",")]
    initiative_view = InitiativeView(character_list)
    await interaction.response.send_message("Combat started! Roll initiative!",
                                            view=initiative_view)
    await initiative_view.wait()
    await interaction.edit_original_response(view=None)
    if not initiative_view.is_full:
        await interaction.edit_original_response(content="Battle cancelled.")
        return
    initiative_list = list(initiative_view.initiatives.items())
    initiative_list.sort(key=lambda a: a[1], reverse=True)
    initiative_string = "\n".join(f"{char.name}: {initiative}" for char, initiative in initiative_list)
    await interaction.channel.send(content=f"```\n{initiative_string}```")
    # TODO: continue battle turns from here...
