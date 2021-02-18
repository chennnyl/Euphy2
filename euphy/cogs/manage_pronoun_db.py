from ..util.db import *

import discord
import discord.ext.commands as commands
import datetime

class PronounDBManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dialogue_users = dict()
        self.confirming = dict()

    def create_progress_embed(self, index):

        titles = [
            "(1/6) Nominative Form",
            "(2/6) Objective Form",
            "(3/6) Possessive Form",
            "(4/6) Possessive Pronoun Form",
            "(5/6) Reflexive Form",
            "(6/6) Plural Pronoun?"
        ]
        descriptions = [
            "This is the pronoun used when the person is the __subject__ of the sentence. Examples:\n- **They** walked to the store.\n- **He** is my best friend.",
            "This is the pronoun used when the person is the __object__ of the sentence. Examples:\n- I talked to **xem** yesterday.\n- I glanced over to **her**.",
            "This is an adjective used when describing __something that belongs to the person__. Examples:\n- This is **aer** bag.\n- Have you seen **xyr** phone?",
            "This is the __pronoun form__ of the possessive, rather than the adjective. Examples:\n- That book is **kits**.\n- **His** is the closest one.",
            "This is the pronoun used when __describing someone's self__, or when they are __both the subject and object__. Examples:\n- He thinks highly of **himself**.\n- Those two keep mostly to **themselves**.",
            "This describes whether a pronoun is grammatically plural. This is very rare, so if you're not sure, just reply with `false`! Examples:\n- They **are** a friend of mine.\n- What **are** they saying? (vs. \"What **is** he saying?\")"
        ]

        return discord.Embed.from_dict({
                "title":titles[index],
                "type":"rich",
                "description":descriptions[index],
                "footer": {
                    "text": f"Reply with \"stop\" to cancel",
                },
            })

        """
                
                "author": {
                    "name": "Euphy2 Pronoun Database",
                    "icon_url": self.bot.user.avatar_url
                }
        """

    # search db
    @commands.command(name="search")
    async def search(self, ctx, *, args=""):
        if args == "":
            await ctx.send("You need to tell me what to search for!")
        else:
            await ctx.send("Sorry, that's not ready yet.")

    # add pronouns to the databse
    @commands.command(name="contribute")
    async def contribute(self, ctx, *, args=""):
        # trigger dialogue tree
        if args == "":

            if ctx.author.id in self.dialogue_users:
                await ctx.send("You're already adding a pronoun set!")
                return
            
            self.dialogue_users[ctx.author.id] = []

            await ctx.send(
                "Let's get started! Start by **replying to this message with the arrow icon** with the nominative form of your pronoun set!",
                embed=self.create_progress_embed(0)
            )

        # insert in one (two) message
        else:

            info = args.split(" ")
            if info[-1].strip().upper() not in ["TRUE","FALSE"]:
                await ctx.send("I don't understand that last bit -- needs to be `true` or `false`!")
                return
            info[-1] = 1 if info[-1].strip().upper() == "TRUE" else 0
            if len(info) != 6:
                await ctx.send("Invalid number of arguments! You must specify all pronouns at once!")
            else:
                self.dialogue_users[ctx.author.id] = info
                self.confirming[ctx.author.id] = True
                await ctx.send(f"Alright! **Reply to this message with the arrow icon** with the text `confirm` to confirm the pronoun set `{'/'.join(info[:-1])}` is correct or with `stop` to cancel!")


    @commands.Cog.listener()
    async def on_message(self, message):

        # check if user is replying to euphy
        if message.reference:
            originalMessage = await message.channel.fetch_message(message.reference.message_id)
             
            if message.author.id in self.dialogue_users and originalMessage.author.id == self.bot.user.id:

                if message.content.strip().upper() == "STOP":
                    self.dialogue_users.pop(message.author.id, None)
                    await message.add_reaction("\N{THUMBS UP SIGN}")

                if len(self.dialogue_users[message.author.id]) < 5:
                    self.dialogue_users[message.author.id].append(message.content)
                elif not self.confirming.get(message.author.id, False):
                    if message.content.strip().upper() not in ["TRUE","FALSE"]:
                        await message.channel.send("Bad input! Try again.")
                    else:
                        self.dialogue_users[message.author.id].append(1 if message.content.strip().upper() == "TRUE" else 0)
                progress = self.dialogue_users[message.author.id]
                if len(progress) < 5:
                    await originalMessage.edit(content="**Reply to this message** with the pronoun corresponding to the following description:",embed=self.create_progress_embed(len(progress)))
                elif len(progress) == 5:
                    await originalMessage.edit(content="Last but not least! Simply reply with **true** or **false** based on the following description:",embed=self.create_progress_embed(len(progress)))
                elif len(progress) == 6 or self.confirming.get(message.author.id, False):
                    with PronounDBCursor() as pronoundb:
                        exists, _, _ = pronoundb.get_pronouns(*self.dialogue_users[message.author.id][:-1])
                        if exists:
                            await message.channel.send(f"You've duplicated some or all of a preexisting pronoun set! Conflicts with `{'/'.join(tuple(exists[0])[1:-1])}`")
                        else:
                            if pronoundb.add_pronouns(*self.dialogue_users[message.author.id]):
                                if self.confirming.get(message.author.id, False):
                                    progress = progress[1:]
                                await message.channel.send(f"Success! `{'/'.join(progress[:-1])}` has been added to my database!")
                            else:
                                await message.channel.send("How bizarre... something went wrong!")
                            self.dialogue_users.pop(message.author.id,None)
                            self.confirming.pop(message.author.id,None)

                
                
                

        