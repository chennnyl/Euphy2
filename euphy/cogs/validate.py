# implements e$try, allowing users to try new names and pronouns
# you know, the whole conceit of the bot

from euphy.util.db import *
from euphy.util.sentence_parsing import Sentence

import discord
import discord.ext.commands as commands

import re

class TryPronouns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # tries three approaches: names + pronouns, then just pronouns; after that, just thinks is name set
    @commands.command(name="try")
    async def try_name_pronouns(self, ctx, *, args=""):
        arg_parser = re.compile(R"(?P<pronouns>[^,/\n\s]+(?:/[^,/\n\s]+)*)\s(?P<names>.+(?:,\s?.+)*)")
        just_pronouns = re.compile(R"(?P<pronouns>[^/\n\s]+(?:/[^/\n\s]+)+)")
        just_names = re.compile(R"(?P<names>.+)")

        if args != "":
            match = arg_parser.match(args)
            if not match:
                match = just_pronouns.match(args)
            if not match:
                match = just_names.match(args)

            userinfo = {"pronouns": None, "names": None} | match.groupdict() # PEP 584 added dict union operator
            if userinfo["pronouns"]:
                userinfo["pronouns"] = userinfo["pronouns"].split("/")
            if userinfo["names"]:
                userinfo["names"] = re.sub(",\s*",",",userinfo["names"]).split(",")
        else:
            userinfo = {"pronouns": None, "names": None}

        # fill in missing info from user database
        if None in [userinfo[key] for key in userinfo]:
            for key in userinfo:
                with UserDBCursor() as userdb:
                    dbinfo = userdb.get_row(ctx.author.id)
                    if dbinfo is None:
                        await ctx.send("I don't have enough info on you to fill in your names and pronouns! Use `e$names` and `e$pronouns` to fix this!")
                        return
                    if userinfo[key] is None:
                        if dbinfo[key] is None:
                            await ctx.send(f"You don't have any {key}! Use `e${key}` to fix this!")
                            return
                        userinfo[key] = dbinfo[key].split(";")

        # at this point we now have names and pronouns, both lists of strings
        with PronounDBCursor() as pronoundb:
            pronouns, allFound, notFound = pronoundb.get_pronouns(*userinfo["pronouns"])
            if not allFound:
                await ctx.send(f"I don't have support for some of those pronouns! I couldn't find: `{', '.join(notFound)}`. Contribute to my pronoun database with `e$contribute`!")
                return 
        with SentenceDBCursor() as sentencedb:
            randomsentence = sentencedb.get_random_sentence()["sentence"]
        
        # pass pronouns and names to sentence handler to interweave
        sentence = Sentence(randomsentence).process_all(pronouns, userinfo["names"])

        await ctx.send(sentence)

        

    
