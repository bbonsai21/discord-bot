import sqlite3 as sql
from typing import Optional

from disnake.ext import commands
from disnake import ApplicationCommandInteraction as ACI, Message, Member, ui, ButtonStyle, Embed, Color
from disnake import MessageInteraction as MI

from privileges import check_admin
from shared import SERVER_GUILD_ID, RESTRICTED, NOT_IMPLEMENTED, discord_format

from db_utils import *

slurs = ["nigg", "nigger", "neega", "niga", "nigga", "niggr", "negro", "negr", "niggar", "ngga", "nga", "nega", "negar"]
n_authorised = []
with open("n_pass.txt", "r+") as f:
    n_authorised = [int(line.strip()) for line in f.readlines()]

def save_NAuthorised():
    with open("n_pass.txt", "w") as f:
        for id in n_authorised:
            f.write(str(id) + "\n")

# castest, from lowest to highest
CASTES = ("Dalits", "Sudra", "Vaisyas", "Kshatriyas", "Brahmins")

class Item:
    def __init__(self, name: str, price: int, description: Optional[str] = ""):
        self.name = name
        self.description = description
        self.price = price

    def set_price(self, price: int):
        self.price = price

    def set_name(self, name: str):
        self.name = name

    def set_desc(self, description: str):
        self.description = description

class Shop:
    def __init__(self, shop_name: str):
        self.items = []
        self.shop_name = shop_name

    def add_item(self, item: Item):
        if item in self.items:
            return False
        
        self.items.append(item)
        return True

    def remove_item(self, item: Item):
        if item in self.items:
            self.items.remove(item)
            return True
        
        return False
    
    def get_shop_name(self):
        return self.shop_name

    def get_all(self):
        return self.items.copy()

class ShopView(ui.View):
    def __init__(self, shop: Shop, user_id: int):
        super().__init__(timeout=30)
        self.shop = shop
        self.user_id = user_id
        self.items = shop.get_all()
        self.current = 0
        self.empty = False

        if not self.items:
            self.empty = True
            return

        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        items = self.items
        can_buy = db_get_user(self.user_id)[0] >= items[self.current].price

        prev_btn = ui.Button(
            label="Previous",
            style=ButtonStyle.green if self.current > 0 else ButtonStyle.gray,
            disabled=self.current <= 0,
        )
        async def go_prev(interaction):
            self.current -= 1
            self.update_buttons()
            await interaction.response.edit_message(view=self)
        prev_btn.callback = go_prev
        self.add_item(prev_btn)

        buy_btn = ui.Button(
            label="Buy",
            style=ButtonStyle.green if can_buy else ButtonStyle.gray,
            disabled=not can_buy,
        )
        async def buy_func(interaction):
            can_buy = db_get_user(self.user_id)[0] >= items[self.current].price
            if not can_buy:
                await interaction.response.send_message("You can't afford this.", ephemeral=True)
                return
            db_add_bal(self.user_id, - items[self.current].price)
            db_add_item(self.user_id, items[self.current].name)
            self.update_buttons()
            await interaction.response.send_message(f"Bought {items[self.current].name}", ephemeral=True)
        buy_btn.callback = buy_func
        self.add_item(buy_btn)

        next_btn = ui.Button(
            label="Next",
            style=ButtonStyle.green if self.current < len(items) - 1 else ButtonStyle.gray,
            disabled=self.current >= len(items) - 1,
        )
        async def go_next(interaction):
            self.current += 1
            self.update_buttons()
            await interaction.response.edit_message(view=self)
        next_btn.callback = go_next
        self.add_item(next_btn)

# SHOPS
PajeetShop = Shop("Pajeet Shop")

# TIMEOUTS
DAILY_TIMEOUT = 24*60*60 # seconds to wait between a daily claim and the next one

# INTERACTIONS
class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg: Message):
        if msg.author.bot:
            return
        
        for s in slurs:
            if s in msg.content.lower():
                if msg.author.id in n_authorised:
                    return
                
                await msg.delete()
                await msg.channel.send(f"<@{msg.author.id}> you first need to buy the n-word pass (use `/shop`).")
                return

    @commands.slash_command(
        name="give_pass",
        description="Gives a N-Pass to the specified user",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def give_pass(self, interaction: ACI, user: Member):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message(RESTRICTED, ephemeral=True)
            return

        if user.id not in n_authorised:
            slurs.append(user.id)
            with open("n_pass.txt", "a") as f:
                f.write(str(user.id) + "\n")

            await interaction.response.send_message(f"Given N-Pass to <@{user.id}>")
        else:
            await interaction.response.send_message(f"{user.name} already has an N-Pass", ephemeral=True)

    @commands.slash_command(
        name="revoke_pass",
        description="Revokes the N-Pass of the specified user",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def revoke_pass(self, interaction: ACI, user: Member):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message(RESTRICTED, ephemeral=True)
            return

        if user.id not in n_authorised:
            await interaction.response.send_message("User does not have a N-Pass.", ephemeral=True)
            return
        
        n_authorised.remove(user.id)
        save_NAuthorised()
        await interaction.response.send_message("Removed user's N-Pass")
    
    @commands.slash_command(
        name="shop",
        description="Display the shop",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def shop(self, interaction: ACI):
        view=ShopView(PajeetShop, interaction.user.id)
        if view.empty:
            await interaction.response.send_message(discord_format("No items to display.Shop is empty", f"**{PajeetShop.shop_name}**"), ephemeral=True)
            return

        embed = Embed(
            title=f"**{PajeetShop.shop_name}**",
            color=Color.blurple()
        )
        embed.add_field(name="Item", value=view.items[view.current].name)
        embed.add_field(name="Description", value=view.items[view.current].description)
        embed.add_field(name="Price", value=view.items[view.current].price, inline=False)

        await interaction.response.send_message(f"**{PajeetShop.shop_name}**", view=view, embed=embed, ephemeral=True)

    @commands.slash_command(
        name="balance",
        description="Prints your balance",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def balance(self, interaction: ACI):
        db_create_user(interaction.user.id)
        await interaction.response.send_message(discord_format(f"₹{db_get_user(interaction.user.id)[0]}", "**Your balance**"), ephemeral=True)
        
    @commands.slash_command(
        name="inventory",
        description="Prints your inventory",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def inventory(self, interaction: ACI):
        user_id = interaction.user.id
        inv = db_get_inv(user_id)  # noqa: F405
        inv_arr = [f"{item[0]} (x{item[1]})" for item in inv]
        await interaction.response.send_message(discord_format("\n".join(inv_arr), "**Your inventory**"), ephemeral=True)
       
    @commands.slash_command(
        name="sell",
        description="Sells an item from your inventory",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def sell(self, interaction: ACI, item: str, amount: int):
        items = db_get_inv(interaction.user.id)  # noqa: F405
        print(items)

    @commands.slash_command(
        name="give_item",
        description="Give an existing item to a user",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def give_item(self, interaction: ACI, user: Member, item: str, amount: int):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message(RESTRICTED, ephemeral=True)
            return

        # this is just to check the item exists in shop
        itemName = next((i for i in PajeetShop.get_all() if i.name == item), None)
        if not itemName:
            await interaction.response.send_message(f"\"{item}\" not found", ephemeral=True)
            return
        
        db_add_item(user.id, item, amount)  # noqa: F405
        await interaction.response.send_message(f"Given {item} (x{amount}) to <@{user.id}>")
    
    @commands.slash_command(
        name="donate",
        description="Donate rupees to someone",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def donate(self, interaction: ACI, user: Member, amount: int):
        user_id = interaction.user.id
        if db_get_user(user_id)[1] > amount:  # noqa: F405
            db_add_bal(user_id, -amount)  # noqa: F405
            db_add_bal(user.id, amount)  # noqa: F405
            await interaction.response.send_message(discord_format(f"Sent ₹{amount} to {user.name}", "**Donation**"))
            return
        else:
            await interaction.response.send_message("You do not enough rupees", ephemeral=True)
    
    @commands.slash_command(
        name="add_rupees",
        description="Add rupees to someone's balance",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def add_rupees(self, interaction: ACI, user: Member, rupees: int):
        db_add_bal(user.id, rupees)  # noqa: F405
        await interaction.response.send_message(f"Added ₹{rupees} to {user.name}")
        
    @commands.slash_command(
        name="change_age",
        description="Change a user's age",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def change_age(self, interaction: ACI, user: Member, age: int):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message(RESTRICTED)
            return
        
        db_create_user(user.id)
        db_change_age(user.id, age)
        await interaction.response.send_message(f"Changed {user.name}'s age to {age}.")

    @commands.slash_command(
        name="add_item",
        description="Add an item to the shop",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def add_item(self, interaction: ACI, name: str, price: int, description: Optional[str] = ""):
        PajeetShop.add_item(Item(name, price, description))
        await interaction.response.send_message(f"Added {name} to shop!", ephemeral=True)

    #TODO
    @commands.slash_command(
        name="remove_item",
        description="Remove an item from the shop",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def remove_item(self, interaction: ACI, name: str):
        await interaction.response.send_message(NOT_IMPLEMENTED, ephemeral=True)
        return

    # @commands.slash_command(
    #     name="daily",
    #     description="Get the daily reward",
    #     guild_ids=[SERVER_GUILD_ID]
    # )
    # async def daily(self, interaction: ACI):
    #     if db_last_daily(interaction.user.id) >


def setup(bot):
    bot.add_cog(Fun(bot))