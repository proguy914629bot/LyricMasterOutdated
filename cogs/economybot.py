import discord
from discord.ext import commands
import json
import random
import asyncio
import os

os.chdir("/home/gilb/LyricMaster/")

mainshop = [
    {
        "name":"⌚ Watch",
        "realname": "Watch",
        "price":150,
        "description":"Time"
    },
    {
        "name":"<:dm_laptop:790875377466605568> Laptop",
        "realname":"Laptop",
        "price":500,
        "description":"Work & Entertainment"
    },
    {
        "name":"<:dm_phone:790876503113990185> Phone",
        "realname":"Phone",
        "price":1000,
        "description":"Work, Entertainment & Home"
    },
    {
        "name":"<:pc:790879190274408458> PC",
        "realname":"PC",
        "price":1500,
        "description":"Gaming & Entertainment"
    }
]

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#-----------FUNCTIONS-----------#

    async def get_bank_data(self):
        with open('BotRecords/mainbank.json', 'r') as f:
            users = json.load(f)

        return users

    async def open_account(self, user):
        users = await self.get_bank_data()

        if str(user.id) in users:
            return False
        else:
            users[str(user.id)] = {}
            users[str(user.id)]["wallet"] = 750
            users[str(user.id)]["bank"] = 250

        with open('BotRecords/mainbank.json', 'w') as f:
            json.dump(users, f, indent=4)

    async def update_bank(self, user, change = 0, mode = "wallet"):
        users = await self.get_bank_data()

        users[str(user.id)][str(mode)] += change

        with open('BotRecords/mainbank.json', 'w') as f:
            json.dump(users, f, indent=4)

        bal = [users[str(user.id)]["wallet"],users[str(user.id)]["bank"]]
        
        return bal

    async def buy_this(self,user,item_name,amount):
        item_name = str(item_name).lower()
        name_ = None
        for item in mainshop:
            name = str(item["realname"]).lower()
            if name == item_name:
                name_ = name
                price = item["price"]
                break

        if name_ == None:
            return [False,1]

        cost = price*amount

        users = await self.get_bank_data()

        bal = await self.update_bank(user)

        if bal[0]<cost:
            return [False,2]


        try:
            index = 0
            t = None
            for thing in users[str(user.id)]["bag"]:
                n = thing["item"]
                if n == item_name:
                    old_amt = thing["amount"]
                    new_amt = old_amt + amount
                    users[str(user.id)]["bag"][index]["amount"] = new_amt
                    t = 1
                    break
                index+=1 
            if t == None:
                obj = {"item":item_name , "amount" : amount, "price" : price}
                users[str(user.id)]["bag"].append(obj)
        except:
            obj = {"item":item_name , "amount" : amount, "price" : price}
            users[str(user.id)]["bag"] = [obj]        

        with open("BotRecords/mainbank.json","w") as f:
            json.dump(users,f,indent=4)

        await self.update_bank(user,cost*-1,"wallet")

        return [True,"Worked"]

    async def sell_this(self,user,item_name,amount,price = None):
        item_name = item_name.lower()
        name_ = None
        for item in mainshop:
            name = item["name"].lower()
            if name == item_name:
                name_ = name
                if price==None:
                    price = 0.9* item["price"]
                break

        if name_ == None:
            return [False,1]

        cost = price*amount

        users = await self.get_bank_data()

        bal = await self.update_bank(user)


        try:
            index = 0
            t = None
            for thing in users[str(user.id)]["bag"]:
                n = thing["item"]
                if n == item_name:
                    old_amt = thing["amount"]
                    new_amt = old_amt - amount
                    if new_amt < 0:
                        return [False,2]
                    users[str(user.id)]["bag"][index]["amount"] = new_amt
                    t = 1
                    break
                index+=1 
            if t == None:
                return [False,3]
        except:
            return [False,3]    

        with open("BotRecords/mainbank.json","w") as f:
            json.dump(users,f,indent=4)

        await self.update_bank(user,cost,"wallet")

        return [True,"Worked"]

#-----------COMMANDS-----------#

    @commands.command(aliases = ['bal'])
    async def balance(self, ctx, member : discord.Member = None):
        if member == None:
            member = ctx.author

        if member.bot:
            await ctx.send('Bro, HE IS A BOT! He cannot run any commands!')
            return

        await self.open_account(member)
        
        users = await self.get_bank_data()

        wallet_amt = users[str(member.id)]["wallet"]

        bank_amt = users[str(member.id)]["bank"]

        total_amt = round(wallet_amt + bank_amt)

        em = discord.Embed(
            title = f"{member.name}#{member.discriminator}'s Balance",
            color = discord.Color.blue(),
            description = f'Wallet: {str(wallet_amt)} <:lm_musiccoin:790888156966682634>\nBank: {str(bank_amt)} <:lm_musiccoin:790888156966682634>\nTotal: {str(total_amt)} <:lm_musiccoin:790888156966682634>'
        )
        em.set_thumbnail(url = member.avatar_url)

        await ctx.send(embed=em)

    @commands.command(aliases = ['with', 'w'])
    async def withdraw(self, ctx, amount = None):
        await self.open_account(ctx.author)
        if amount == None:
            await ctx.send(f"Please enter the amount needed!")
            return
        
        bal = await self.update_bank(ctx.author)
        if amount == "all":
            amount = bal[1]
        if amount == "max":
            amount == bal[1]


        try:
            amount = int(amount)
        except:
            await ctx.send(f'Please put the amount as a number!')
            return

        if amount < 0:
            await ctx.send(f'Amount must be positive!')
            return

        if amount > bal[1]:
            await ctx.send('You don\'t have that much money in your bank account! Try checking ur balance!')
            return

        await self.update_bank(ctx.author, amount)
        await self.update_bank(ctx.author, -1*amount, "bank")

        await ctx.send(f'You just withdrawed {amount} <:lm_musiccoin:790888156966682634>!')

    @commands.command(aliases = ['inventory', 'inv'])
    async def bag(self, ctx, member : discord.Member = None):
        if member == None:
            member = ctx.author
        await self.open_account(member)
        user = member
        users = await self.get_bank_data()

        try:
            bag = users[str(user.id)]["bag"]
        except:
            bag = []


        em = discord.Embed(title = f"{member.name}'s Inventory:", color = ctx.author.color)
        if bag == []:
            embed = discord.Embed(
                title = f"{member.name}'s Inventory:",
                description = f'{member.name}#{member.discriminator} has nothing in their inventory! Go buy some stuff by using the `lm!buy <Item> <Amount>` and to see the shop, do the `lm!shop` command!',
                color = ctx.author.color
            )
            await ctx.send(embed=embed)
            return
        for item in bag:
            name = str(item["item"]).title()
            amount = item["amount"]
            priceeach = item["price"]

            em.add_field(name = name, value = 'Amount: ' + str(amount) + '\nPrice Each: $cd ' + str(priceeach), inline = False) 

        await ctx.send(embed = em)

    @commands.command()
    async def buy(self,ctx,item,amount = 1):
        await self.open_account(ctx.author)

        res = await self.buy_this(ctx.author,item,amount)

        if not res[0]:
            if res[1]==1:
                await ctx.send("That Object isn't there!")
                return
            if res[1]==2:
                await ctx.send(f"You don't have enough money in your wallet to buy {amount} {item}")
                return


        await ctx.send(f"You just bought {amount} {item}")

    @commands.command(aliases = ['dep', 'd'])
    async def deposit(self, ctx, amount = None):
        await self.open_account(ctx.author)
        if amount == None:
            await ctx.send(f"Please enter the amount needed!")
            return
        
        bal = await self.update_bank(ctx.author)

        if amount == "all":
            amount = bal[0]
        if amount == "max":
            amount = bal[0]

        try:
            amount = int(amount)
        except:
            await ctx.send(f'Please put the amount as a number!')
            return

        if amount < 0:
            await ctx.send(f'Amount must be positive!')
            return

        if amount > bal[0]:
            await ctx.send('You don\'t have that much money in your bank account! Try checking ur balance!')
            return

        await self.update_bank(ctx.author, amount, "bank")
        await self.update_bank(ctx.author, -1*amount)

        await ctx.send(f'You just deposited {amount} <:lm_musiccoin:790888156966682634>!')

    @commands.command()
    async def sell(self,ctx,item,amount = 1):
        await self.open_account(ctx.author)

        res = await self.sell_this(ctx.author,item,amount)

        if not res[0]:
            if res[1]==1:
                await ctx.send("That Object isn't there!")
                return
            if res[1]==2:
                await ctx.send(f"You don't have {amount} {item} in your inventory.")
                return
            if res[1]==3:
                await ctx.send(f"You don't have {item} in your inventory.")
                return

        await ctx.send(f"You just sold {amount} {item}.")

    @commands.command()
    async def shop(self, ctx):
        embed = discord.Embed(
            title = f"Shop from LyricMaster's shop!",
            color = ctx.author.color, 
            description = f'Note that these items are currently useless and not useable and just for safe-keeping for later!'
        )
        for item in mainshop:
            name = item["name"]
            price = item["price"]
            desc = item["description"]
            embed.add_field(
                name = name,
                value = f'Price: ${str(price)} | {str(desc)}',
                inline = False
            )
        embed.set_footer(
            text = f'You can purchase items by doing lm!buy <Item Name> <Amount (Default is 1)>'
        )
        
        await ctx.send(embed=embed)

    @commands.command(aliases = ['lb'])
    async def leaderboard(self,ctx,x = 5):
        users = await self.get_bank_data()
        leader_board = {}
        total = []
        for user in users:
            name = int(user)
            total_amount = users[user]["wallet"] + users[user]["bank"]
            leader_board[total_amount] = name
            total.append(total_amount)

        total = sorted(total,reverse=True)    

        em = discord.Embed(title = f"Top {x} Richest People" , description = "This is decided on the basis of raw money in the bank and wallet",color = discord.Color(0xfa43ee))
        index = 1
        for amt in total:
            id_ = leader_board[amt]
            member = self.bot.get_user(id_)
            name = member.name
            em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False)
            if index == x:
                break
            else:
                index += 1

        await ctx.send(embed = em)

    @commands.command(aliases = ['give'])
    async def share(self, ctx, member:discord.Member, amount = None):
        await self.open_account(ctx.author)

        if member.bot:
            await ctx.send('Bro, HE IS A BOT! He cannot run any commands!')
            return

        await self.open_account(member)

        if amount == None:
            await ctx.send(f"Please enter the amount needed!")
            return
        
        bal = await self.update_bank(ctx.author)
        if amount == "all":
            amount = bal[1]
        if amount == "max":
            amount = bal[1]

        try:
            amount = int(amount)
        except:
            await ctx.send(f'Please put the amount as a number!')
            return
        
        if amount == 0:
            await ctx.send(f'Don\'t put the amount as `0` please!')
            return

        if amount < 0:
            await ctx.send(f'Amount must be positive!')
            return

        if amount > bal[1]:
            await ctx.send('You don\'t have that much money in your bank account! Try checking ur balance!')
            return

        await self.update_bank(ctx.author, -1*amount)
        await self.update_bank(member, amount)

        await ctx.send(f'You just gave {member.name}#{member.discriminator} {amount} <:lm_musiccoin:790888156966682634>!')

    @commands.command()
    async def rob(self, ctx, member:discord.Member):
        await self.open_account(ctx.author)

        if member.bot:
            await ctx.send('Bro, HE IS A BOT! He cannot run any commands!')
            return
        
        await self.open_account(member)
        
        bal = await self.update_bank(member)
        bals = await self.update_bank(ctx.author)
        
        if bals[0] <= 999:
            await ctx.send(f'You need 1000 <:lm_musiccoin:790888156966682634> in your wallet to rob someone. Withdraw some <:lm_musiccoin:790888156966682634> first!')
            return
        if bal[0] < 1001:
            await ctx.send(f'The rob isn\'t worth it!')
            return

        earnings = random.randrange(0, bal[0])

        if earnings == 0:
            await ctx.send(f'You got caught and paid 1000 <:lm_musiccoin:790888156966682634> to the Police for an unsucsessful robbery!')
            await self.update_bank(ctx.author, 1000 - bals[0])
            return

        await self.update_bank(ctx.author,earnings)
        await self.update_bank(member, -1*earnings)

        try:
            await member.send(f'Oh No! {ctx.author.name}#{ctx.author.discriminator} robbed {earnings} <:lm_musiccoin:790888156966682634> in {ctx.guild.name} server in channel {ctx.channel.mention}!')
        except:
            pass
        await ctx.send(f'You robbed {member.name}#{member.discriminator} and got {earnings} <:lm_musiccoin:790888156966682634>!')

    @commands.command()
    async def beg(self, ctx):
        await self.open_account(ctx.author)

        users = await self.get_bank_data()

        earnings = random.randrange(0, 100)
        if earnings != 0:
            await ctx.send(f'Hey! Someone gave you {earnings} <:lm_musiccoin:790888156966682634>!')
        else:
            await ctx.send(f'Hey! No one came to you to donate some coins... Bad Luck..')
            return

        users[str(ctx.author.id)]["wallet"] += earnings

        with open('BotRecords/mainbank.json', 'w') as f:
            json.dump(users, f, indent=4)

def setup(bot):
    bot.add_cog(Economy(bot))
    print('Economy Cog Is Ready!')