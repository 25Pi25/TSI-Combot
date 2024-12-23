import numpy as np
from discord import Interaction

from src.constants import CHARACTER_LIMIT, client


def dice_roll(throws: int, sides: int):
    if throws < 1 or throws > 10_000:
        return "Throws must be between 1-10,000."
    if sides < 1 or sides > 10_000_000:
        return "Sides must be between 1-10,000,000."

    # np randint doesn't support 1-1 randint for some reason
    results = np.random.randint(1, sides, throws) if sides > 1 else [1] * throws
    total = np.sum(results)

    # the format is not complete still, because {results} could be omitted
    roll_text = f"{throws}d{sides} resulted in {{results}} for a sum of {total}"
    large_text = roll_text.format(results=",".join(map(str, results)))
    if len(large_text) <= CHARACTER_LIMIT:
        return large_text
    truncated_text = roll_text.format(results="[...]")
    if len(truncated_text) <= CHARACTER_LIMIT:
        return truncated_text
    return "Too big!"


@client.tree.command()
async def roll(interaction: Interaction, throws: int, sides: int):
    """Rolls dice."""
    print(f'{interaction.user.display_name} rolled {throws}d{sides}')
    # I should probably stop throwing random numbers out there but ideally defer this bc rolls take time to compute
    if throws > 1000:
        await interaction.response.defer()
        await interaction.followup.send(dice_roll(throws, sides))
    else:
        await interaction.response.send_message(dice_roll(throws, sides))