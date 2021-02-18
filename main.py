from euphy.cogs.manage_pronoun_db import PronounDBManagement
from euphy.cogs.user_settings import ModifyNamesPronouns
from euphy.cogs.validate import TryPronouns



import discord
import discord.ext.commands as commands

import os

from dotenv import load_dotenv
load_dotenv()



# TODO: help command, comment throughout, search pronoun db (paginated?)
bot = commands.Bot(command_prefix="e$")

@bot.event
async def on_ready():
    print("Connected to Discord!")
    await bot.change_presence(activity=discord.Game("e$ - Euphy 2 (0.1.0)"), status=discord.Status.online)

bot.add_cog(PronounDBManagement(bot))
bot.add_cog(ModifyNamesPronouns(bot))
bot.add_cog(TryPronouns(bot))

bot.run(os.getenv("DBOT_TOKEN"))
