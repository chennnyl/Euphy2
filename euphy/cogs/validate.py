# implements e$try, allowing users to try new names and pronouns
# you know, the whole conceit of the bot

from euphy.util.db import *
from euphy.util.sentence_parsing import Sentence

import discord
import discord.ext.commands as commands

import asyncio
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
            

            dtt = lambda d: tuple(d[a] for a in ["nom","obj","poss","posspro","ref","id"])

            plist = []
            psets = []
            conflicts = {}
            for pset in pronouns:
                pset = dtt(pset)
                for pronoun in pset[:-1]:
                    if pronoun in plist:
                        if not conflicts.get(pronoun, False):
                            conflicts[pronoun] = [pset, psets[plist.index(pronoun)]]
                        else:
                            conflicts[pronoun].append(pset)
                    
                    plist.append(pronoun)
                    psets.append(pset)
            
            def unique_tuples(d, key):
                already = []
                for t in d[key]:
                    if t not in already:
                        already.append(t)
                return len(already)

            conflicts = {key:conflicts[key] for key in conflicts if unique_tuples(conflicts, key) > 1}

            while True:
                for conflict in conflicts:
                    if len(conflicts[conflict]) > 9:
                        await ctx.send("Wow, that's a lot of conflict -- I can't handle that right now, ask Lynne about it.")
                        return
                    
                    indicators = [
                        "\N{REGIONAL INDICATOR SYMBOL LETTER A}",
                        "\N{REGIONAL INDICATOR SYMBOL LETTER B}",
                        "\N{REGIONAL INDICATOR SYMBOL LETTER C}",
                        "\N{REGIONAL INDICATOR SYMBOL LETTER D}",
                        "\N{REGIONAL INDICATOR SYMBOL LETTER E}",
                        "\N{REGIONAL INDICATOR SYMBOL LETTER F}",
                        "\N{REGIONAL INDICATOR SYMBOL LETTER G}",
                        "\N{REGIONAL INDICATOR SYMBOL LETTER H}",
                        "\N{REGIONAL INDICATOR SYMBOL LETTER I}",
                    ]

                    header = "Looks like we have some pronouns that could refer to multiple sets! Let's work through those.\n**React with the number corresponding to the set you meant!**\n"
                    msg = await ctx.send(
                        content=None,
                        embed=discord.Embed.from_dict({
                            "title": "Pronoun Conflict Resolution",
                            "description":header + "\n".join(f"`{i+1}. {'/'.join(pset[:-1])}`" for i,pset in enumerate(conflicts[conflict]))
                        }))
                    [await msg.add_reaction(indicators[i]) for i,_ in enumerate(conflicts[conflict])]
                    
                    check = lambda reaction, user: reaction.message.id == msg.id and user.id == ctx.author.id and reaction.emoji in indicators
                    try:
                        reaction, _ = await ctx.bot.wait_for('reaction_add',timeout=120,check=check)
                        await msg.delete()
                        
                        # indicators.index(reaction.emoji)
                        for cpro in [cpro for cpro in conflicts[conflict] if cpro[-1] != conflicts[conflict][indicators.index(reaction.emoji)][-1]]:
                            idToRemove = cpro[-1]
                            pronounToRemove = [p for p in pronouns if p["id"] == idToRemove][0]
                            pronouns.remove(pronounToRemove)
                        

                    except asyncio.TimeoutError:
                        await msg.edit(content="This message was removed to conserve bot resources.")


                break

        with SentenceDBCursor() as sentencedb:
            randomsentence = sentencedb.get_random_sentence()["sentence"]
        
        # pass pronouns and names to sentence handler to interweave
        sentence = Sentence(randomsentence).process_all(pronouns, userinfo["names"])

        await ctx.send(sentence)

        

    
