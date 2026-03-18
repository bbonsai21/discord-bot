import sqlite3 as sql
from typing import Optional

from disnake.ext import commands
from disnake import ApplicationCommandInteraction as ACI, Message, Member, ui, ButtonStyle
from disnake import MessageInteraction as MI

from privileges import check_admin
from shared import SERVER_GUILD_ID, RESTRICTED, NOT_IMPLEMENTED, SHOP_DB_PATH, discord_format

slurs = ["nigg", "nigger", "neega", "niga", "nigga", "niggr", "negro", "negr", "niggar", "ngga", "nga", "nega", "negar"]
n_authorised = []
with open("n_pass.txt", "r+") as f:
    n_authorised = [int(line.strip()) for line in f.readlines()]

def save_NAuthorised():
    with open("n_pass.txt", "w") as f:
        for id in n_authorised:
            f.write(str(id) + "\n")

# setting up the SQL server
db = sql.connect(SHOP_DB_PATH)
db_cursor = db.cursor()
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    balance INTEGER,
    items TEXT,
    caste TEXT,
    age INTEGER  
)
""")
db.commit()
db.close()

# castest, from lowest to highest
CASTES = ("Dalits", "Sudra", "Vaisyas", "Kshatriyas", "Brahmins")

def create_user(userID: int):
    conn = sql.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, balance, items, caste, age) VALUES (?, 0, '', 'Dalits', 18)", (userID,))
    conn.commit()
    conn.close()

def get_user(userID: int):
    create_user(userID)

    conn = sql.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT balance, items, caste, age FROM users WHERE id = ?", (userID,))
    row = cursor.fetchone()
    conn.close()
    return row

def add_bal(userID: int, amount: int):
    conn = sql.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, userID,))
    conn.commit()
    conn.close()

def db_change_age(userID: int, age: int):
    conn = sql.connect(SHOP_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET age = ? WHERE id = ?", (age, userID,))
    conn.commit()
    conn.close()

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
        bal = get_user(self.user_id)[0]
        can_buy = bal >= items[self.current].price

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
            label=f"Buy {items[self.current].name} ({items[self.current].price})",
            style=ButtonStyle.green if can_buy else ButtonStyle.gray,
            disabled=not can_buy,
        )
        async def buy_func(interaction):
            if not can_buy:
                await interaction.response.send_message("You can't afford this.", ephemeral=True)
                return
            add_bal(self.user_id, -items[self.current].price)
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
            await interaction.response.send_message(RESTRICTED)
            return

        if user.id not in n_authorised:
            slurs.append(user.id)
            with open("n_pass.txt", "a") as f:
                f.write(str(user.id) + "\n")

            await interaction.response.send_message(f"Given N-Pass to <@{user.id}>")
        else:
            await interaction.response.send_message(RESTRICTED)

    @commands.slash_command(
        name="revoke_pass",
        description="Revokes the N-Pass of the specified user",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def revoke_pass(self, interaction: ACI, user: Member):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message(RESTRICTED)
            return

        if user.id not in n_authorised:
            await interaction.response.send_message("User does not have a N-Pass.")
            return
        
        n_authorised.remove(user.id)
        save_NAuthorised()
        await interaction.response.send_message("Removed user's N-Pass")
    
    # TODO
    @commands.slash_command(
        name="shop",
        description="Display the shop",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def shop(self, interaction: ACI):
        view=ShopView(PajeetShop, interaction.user.id)
        if view.empty:
            await interaction.response.send_message(discord_format("No items to display.Shop is empty", f"**{PajeetShop.shop_name}**"))
        else:
            await interaction.response.send_message(discord_format(PajeetShop.get_all()[view.current].name, f"**{PajeetShop.shop_name}**"), view=view)

    @commands.slash_command(
        name="balance",
        description="Prints your balance",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def balance(self, interaction: ACI):
        create_user(interaction.user.id)
        await interaction.response.send_message("Your balance is: ₹" + str(get_user(interaction.user.id)[0]))
        
    @commands.slash_command(
        name="add_rupees",
        description="Add rupees to someone's balance",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def add_rupees(self, interaction: ACI, user: Member, rupees: int):
        add_bal(user.id, rupees)
        await interaction.response.send_message("Added ₹" + str(rupees) + " to " + str(user.name))
        
    @commands.slash_command(
        name="change_age",
        description="Change a user's age",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def change_age(self, interaction: ACI, user: Member, age: int):
        if not check_admin(interaction.user.id):
            await interaction.response.send_message(RESTRICTED)
            return
        
        create_user(user.id)
        db_change_age(user.id, age)
        await interaction.response.send_message(f"Changed {user.name}'s age to {age}.")

    @commands.slash_command(
        name="add_item",
        description="Add an item to the shop",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def add_item(self, interaction: ACI, name: str, price: int, description: Optional[str] = ""):
        PajeetShop.add_item(Item(name, price, description))
        await interaction.response.send_message(f"Added {name} to shop!")



def setup(bot):
    bot.add_cog(Fun(bot))