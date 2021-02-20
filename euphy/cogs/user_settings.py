from ..util.db import *

import discord
import discord.ext.commands as commands
import re

# Pass comma- or slash-delineated list straight to command

class SlashList(commands.Converter):
    async def convert(self, ctx, argument):
        return re.sub(R"/\s*", "/", argument).split("/")

class CommaList(commands.Converter):
    async def convert(self, ctx, argument):
        return re.sub(R",\s*", ",", argument).split(",")

class ModifyNamesPronouns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command for removing stored info

    @commands.command(name="delete")
    async def delete_command(self, ctx, field=""):
        if field == "":
            await ctx.send("You need to tell me what you want to delete! (Acceptable values are `names` and `pronouns`)")
            return
        if field not in ["names","pronouns"]:
            await ctx.send(f"I don't know what `{field}` is: you can only delete `names` and `pronouns`!")

        with UserDBCursor() as userdb:
            unames = userdb.get_row(ctx.author.id)

            if unames is None or unames["names"] is None:
                await ctx.send("You don't have any names set! Use `e$name` to fix that!")
                return
            else:
                if userdb.set_field(ctx.author.id, None, field):
                        await ctx.send(f"Got it! Your {field} have been removed.")
                else:
                    await ctx.send(f"Something went wrong; I couldn't remove your {field}.")
        

    
    # Set your names in the DB

    @commands.command(name="names")
    async def names(self, ctx, *, names: CommaList=""):
        with UserDBCursor() as userdb:
            if names == "":
                unames = userdb.get_row(ctx.author.id)

                print(unames)

                if unames is None or unames["names"] is None:
                    await ctx.send("You don't have any names set! Use `e$names` to fix that!")
                    return
                else:
                    unames = unames['names'].split(";")
            
                if len(unames) == 2:
                    send = "Your names are set to " + " and ".join(unames)
                elif len(unames) > 2:
                    unames[-1] = "and " + unames[-1]
                    send = "Your names are set to " + ", ".join(unames)
                else:
                    send = "Your name is set to " + unames[0]
                
                await ctx.send(send + ". Use `e$names` to modify them!")
            else:

                if userdb.set_field(ctx.author.id, names, "names"):
                    await ctx.send("Got it! Your names have been updated.")
                else:
                    await ctx.send("Something went wrong; I couldn't update your names.")
    
    @commands.command(name="pronouns")
    async def pronouns(self, ctx, *, pronouns: SlashList = ""):
        with UserDBCursor() as userdb:
            if pronouns == "":
                upronouns = userdb.get_row(ctx.author.id)
                if upronouns is None or upronouns["pronouns"] is None:
                    await ctx.send("You don't have any pronouns set! Use `e$pronouns` to fix that!")
                    return
                else:
                    send = "Your pronouns are set to " + "/".join(upronouns['pronouns'].split(";"))
                
                await ctx.send(send + ". Use `e$pronouns` to modify them!")

            else:
                with PronounDBCursor() as pronoundb:
                    _, allPronounsFound, notFound = pronoundb.get_pronouns(*pronouns)

                if allPronounsFound:
                
                    if userdb.set_field(ctx.author.id, pronouns, "pronouns"):
                        await ctx.send("Got it! Your pronouns have been updated.")
                    else:
                        await ctx.send("Something went wrong; I couldn't update your pronouns.")
                else:
                    await ctx.send("We don't have all of your pronouns... fix yet to come")

            
