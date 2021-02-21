import asyncio

async def paginate(content, ctx, timeout=120, deleteMessage="This message was deleted to conserve bot resources."):

    right_arrow = "\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}"
    left_arrow = "\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}"

    index = 0

    msg = await ctx.send(**content[index])
    if len(content) > 1:
        await msg.add_reaction(right_arrow)

    check = lambda reaction, user: reaction.message.id == msg.id and user.id == ctx.author.id

    while True:
        try:
            reaction, _ = await ctx.bot.wait_for('reaction_add',timeout=timeout,check=check)

            if reaction.emoji == right_arrow and index < len(content)-1:
                index += 1
                await msg.edit(**content[index])
                await msg.clear_reactions()
                await msg.add_reaction(left_arrow)
                if index < len(content)-1:
                    await msg.add_reaction(right_arrow)
                
            elif reaction.emoji == left_arrow and index > 0:
                index -= 1
                await msg.edit(**content[index])
                await msg.clear_reactions()
                if index > 0:
                    await msg.add_reaction(left_arrow)
                await msg.add_reaction(right_arrow)

        except asyncio.TimeoutError:
            try:
                await msg.edit(content=deleteMessage)
                await msg.clear_reactions()
            except:
                pass
            finally:
                break