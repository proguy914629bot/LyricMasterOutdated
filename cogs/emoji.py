import discord
from discord.ext import commands
import aiohttp
import io
from io import BytesIO

class Emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_emoji_from_file(self, ctx, question1 = None):
        try:
            attachment = ctx.message.attachments[0]
        except:
            return await ctx.send("Can't find any attachments!")

        await ctx.send("I got your file! Reading it!")

        if not str(attachment.filename).lower().endswith(('.jpg', '.png', '.gif')):
            return await ctx.send("Unsupported file. Only supports `.jpg`, `.jpeg`, `.png`, and `.gif`!")

        if attachment.size > (256000):
            return await ctx.send("Your file is too big! Try again later but next time, shorten the file!")

        try:
            contents = await attachment.read()
        except (UnicodeDecodeError, discord.HTTPException) as e:
            return await ctx.send("Something went wrong on our end. Try again in a few moments!\n\nError: ```\n{}\n```".format(e))

        if question1 == None:

            await ctx.send("What should be the name of the emoji? Excluding the `:`!")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            ques = await self.bot.wait_for('message', timeout = 60.0, check=check)
            question1 = ques.content

        await ctx.send("Please wait while I create your emoji!")

        try:
            emoji = await ctx.guild.create_custom_emoji(name = f"{str(question1)}", reason = "Created by {}".format(str(ctx.author)))
        except:
            return await ctx.send("Something wen't wrong. Maybe because of these issues!" + f""" ```css
- I am missing the required permissions to create an emoji
- You are missing the required permissions to create an emoji
- You reached your maximum limit of creating emojis
            """)

        embed = discord.Embed()
        embed.title = "New Emoji Created"
        embed.add_field(
            name = "ID:",
            value = str(emoji.animated)
        )
        embed.add_field(
            name = "Unicode:",
            value = f"{f'`<a:{emoji.name}:{emoji.id}>`' if emoji.animated else f'`<:{emoji.name}:{emoji.id}>`'}"
        )
        embed.add_field(
            name = "Is Animated?",
            value = str(emoji.animated)
        )
        embed.add_field(
            name = "Created At:",
            value = emoji.created_at()
        )
        try:
            embed.add_field(
                name = "Created By:",
                value = str(emoji.user)
            )
        except:
            pass

        await ctx.send(embed=embed)

    async def check_url(self, url):
        try:
            async with aiohttp.ClientSession() as sessions:
                async with sessions.get(str(url)) as resp:
                    resp.status == 200
                    return [resp.status, True]
        except aiohttp.ClientError:
            return [404, False]

    async def create_emoji_from_web(self, ctx, web : str, question1 = None):
        data = await self.check_url(web)

        if data == False:
            return await ctx.send("Cannot access that website.")
        elif data == 404:
            return await ctx.send("Cannot access that website.")

        async with aiohttp.ClientSession() as session:
            async with session.get(web) as resp:
                raw_bytes = await resp.read()

        real_bytes = BytesIO(raw_bytes)

        if question1 == None:

            await ctx.send("What should be the name of the emoji? Excluding the `:`!")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            ques = await self.bot.wait_for('message', timeout = 60.0, check=check)
            question1 = ques.content

        await ctx.send("Please wait while I create your emoji!")

        try:
            emoji = await ctx.guild.create_custom_emoji(name = f"{str(question1)}", reason = "Created by {}".format(str(ctx.author)))
        except:
            return await ctx.send("Something wen't wrong. Maybe because of these issues!" + f""" ```css
- I am missing the required permissions to create an emoji
- You are missing the required permissions to create an emoji
- You reached your maximum limit of creating emojis
```
            """)

        embed = discord.Embed()
        embed.title = "New Emoji Created"
        embed.add_field(
            name = "ID:",
            value = str(emoji.animated)
        )
        embed.add_field(
            name = "Unicode:",
            value = f"{f'`<a:{emoji.name}:{emoji.id}>`' if emoji.animated else f'`<:{emoji.name}:{emoji.id}>`'}"
        )
        embed.add_field(
            name = "Is Animated?",
            value = str(emoji.animated)
        )
        embed.add_field(
            name = "Created At:",
            value = emoji.created_at()
        )
        try:
            embed.add_field(
                name = "Created By:",
                value = str(emoji.user)
            )
        except:
            pass

        await ctx.send(embed=embed)

    async def delete_emoji(self, ctx, emoji):
        await ctx.send("Are you sure that you want to delete the `{}` emoji??? Reply with Y/N".format(emoji))

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        reply = await self.bot.wait_for('message', timeout = 60.0, check=check)
        reply = str(reply.content).lower()

        if reply == "y":
            await emoji.delete(reason = "Removed by {}".format(str(ctx.author)))

            await ctx.send("Emoji deleted sucsessfully")
        else:
            await ctx.send("Emoji has not been deleted")

    @commands.group()
    @commands.guild_only()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def emoji(self, ctx):
        if ctx.invoked_subcommand is None:
            if self.bot.get_command("help emoji") != None:
                self.bot.get_command("help emoji")
            else:
                await ctx.send("Something wen't wrong on our end! Try again later!")

    @emoji.error
    async def emoji_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("No private messaging. Sorry!")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(error)
            return
        return

    @emoji.command(aliases = ['make', 'mk'])
    @commands.has_guild_permissions(manage_emojis=True)
    async def create(self, ctx, source = None):
        if source == None:
            if len(ctx.message.attachments) == 1:
                return await self.create_emoji_from_file(ctx)
            
            await ctx.send("Cannot find source for creating an emoji! Please either put an attachment or an web file!")

        return await self.create_emoji_from_web(ctx, str(source))

    @emoji.command(aliases = ['remove', 'rm'])
    @commands.has_guild_permissions(manage_emojis=True)
    async def delete(self, ctx, emoji : discord.Emoji):
        return await self.delete_emoji(ctx, emoji)

    @delete.error
    async def delete_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You are missing the Manage Emoji permission!")
            return

    @create.error
    async def create_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You are missing the Manage Emoji permission!")
            return

    @emoji.command()
    async def info(self, ctx, emoji : discord.Emoji, types = None):
        if types != None:
            embed = discord.Embed()
            embed.set_thumbnail(url = emoji.url)
            embed.title = f"Emoji Info: {emoji.name} - {emoji.id}"
            if str(types).lower() == "name":
                embed.add_field(
                    name = "Name:",
                    value = "{}".format(str(emoji.name))
                )
            elif str(types).lower() == "unicode":
                embed.add_field(
                    name = "Unicode:",
                    value = f"{f'`<a:{emoji.name}:{emoji.id}>`' if emoji.animated else f'`<:{emoji.name}:{emoji.id}>`'}"
                )
            elif str(types).lower() in ("type", "types", "animated"):
                embed.add_field(
                    name = "Is Animated?",
                    value = str(emoji.animated)
                )
            elif str(types).replace("-", "").replace("_", "").replace(".", "").lower() == "createdat":
                embed.add_field(
                    name = "Created At:",
                    value = emoji.created_at()
                )
            elif str(types).replace("-", "").replace("_", "").replace(".", "").lower() == "createdby":
                try:
                    embed.add_field(
                        name = "Created By:",
                        value = str(emoji.user)
                    )
                except:
                    return await ctx.send("You have no permission to view this command!")
            else:
                return await ctx.send("No such type as {}!".format(types))
            return await ctx.send(embed=embed)

        embed = discord.Embed()
        embed.set_thumbnail(url = emoji.url)
        embed.title = f"Emoji Info: {emoji.name} - {emoji.id}"
        embed.add_field(
            name = "Name:",
            value = "{}".format(str(emoji.name))
        )
        embed.add_field(
            name = "ID:",
            value = str(emoji.animated)
        )
        embed.add_field(
            name = "Unicode:",
            value = f"{f'`<a:{emoji.name}:{emoji.id}>`' if emoji.animated else f'`<:{emoji.name}:{emoji.id}>`'}"
        )
        embed.add_field(
            name = "Is Animated?",
            value = str(emoji.animated)
        )
        embed.add_field(
            name = "Created At:",
            value = emoji.created_at()
        )
        try:
            embed.add_field(
                name = "Created By:",
                value = str(emoji.user)
            )
        except:
            pass

        await ctx.send(embed=embed)

    @info.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.EmojiNotFound):
            await ctx.send("Emoji Not Found!")
        elif isinstance(error, discord.Forbidden):
            pass
        return

def setup(bot):
    bot.add_cog(Emoji(bot))
    print("Emoji Cog Is Ready!")