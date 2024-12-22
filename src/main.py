import discord
from discord import Interaction
from src.constants import client, TOKEN

# noinspection PyUnresolvedReferences
from modules import combat, dice, type_matchups

@client.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    # TODO: prevent errors from being unhandled when an interaction doesn't respond back
    pass

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command()
async def hello(interaction: Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')


if __name__ == '__main__':
    client.run(TOKEN)
