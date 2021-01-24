import discord
from discord.ext import commands
import DiscordUtils
import os

os.chdir("/home/gilb/LyricMaster/")

class Invites(commands.Cog): #SOURCE: https://www.youtube.com/watch?v=PhFoekGpqgY
    def __init__(self, bot):
        self.bot = bot
        self.tracker = DiscordUtils.InviteTracker(self.bot)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.tracker.cache_invites()

    @commands.Cog.listener()
    async def on_invite_create(self,invite):
        await self.tracker.update_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        await self.tracker.update_guild_cache(guild)

    @commands.Cog.listener()
    async def on_invite_delete(self,invite):
        await self.tracker.remove_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        await self.tracker.remove_guild_cache(guild)

    @commands.Cog.listener()
    async def on_member_join(self,member):
        inviter = await self.tracker.fetch_inviter(member) # inviter is the member who invited
        data = await self.bot.invites.find(inviter.id)
        if data is None:
            data = {"_id": inviter.id, "count": 0, "userInvited": []}

        data["count"] += 1
        data["usersInvited"].append(member.id)
        await self.bot.invites.upsert(data)

        channel = client
        embed = discord.Embed(
            title=f"Welcome {member.display_name}",
            description=f"Invited by: {inviter.mention}\nInvites of {inviter.mention}: {data['count']}",
            timestamp=member.joined_at
        )
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=member.guild.name, icon_url=member.guild.icon_url)
        await channel.send(embed=embed)
    
    @commands.command(aliases = ['invites'])
    async def invite(self, ctx, args, args2, args3):
        if str(args) == 'invites':
            args2 : discord.Member = None
            if args2 == None:
                args2 = ctx.author
            data = await self.bot.invites.find(ctx.author.id)
            if data["count"] == 0:
                embed = discord.Embed(
                    title = f'{args2.name}#{args2.discriminator}\'s Invites',
                    description = f'{args2.name} currently doesn\'t have any invites!',
                    color = ctx.author.color
                )
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title = f'{args2.name}#{args2.discriminator}\'s Invites',
                description = f'Total Invites: {data["count"]}\n',
                color = ctx.author.color
            )

        if str(args) == 'configure':
            if str(args2) == 'channel':
                args3 : discord.TextChannel = None


    #@commands.command()
    #async def invite(self, ctx, args, args2):
    #    finalargs = str(args).lower()

def setup(bot):
    bot.add_cog(Invite(bot))
    print('Invites Cog Is Ready!')