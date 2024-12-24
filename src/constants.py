import os

from discord import app_commands
from dotenv import load_dotenv
import discord

from tsi_types import Type

load_dotenv()

CHARACTERS_DIR = '../characters'
# using .env particularly because I prefer it and it's more standardized
TOKEN = os.getenv('TOKEN')
GUILD_ID = os.getenv('GUILD')
ADMIN_ID = os.getenv('ADMIN')
BOT_INTENTS = discord.Intents.all()
MY_GUILD = discord.Object(id=GUILD_ID)
CHARACTER_LIMIT = 2000

# CLIENT-SIDE CODE IS HERE
# typechart is a global variable that locates a matchup based on the attacker and defender.
# usage: typechart[Type.ATTACKER][Type.DEFENDER] = float representing the multiplier


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


typechart = load_typechart()


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
