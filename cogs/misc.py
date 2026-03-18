import privileges
from disnake.ext import commands
from disnake import Member
from disnake import ApplicationCommandInteraction as ACI

from shared import SERVER_GUILD_ID, RESTRICTED, NOT_IMPLEMENTED, CMDS

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
    name="terminate",
    description="Terminates the bot",
    guild_ids=[SERVER_GUILD_ID]
    )
    async def terminate(self, interaction: ACI):
        if not privileges.check_admin(interaction.user.id):
            await interaction.send(RESTRICTED)
        
        await interaction.send("Shutting down.")
        await self.bot.close()

    @commands.slash_command(
        name="ping",
        description="Pong! Returns server's ping",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def ping(self, interaction: ACI):
        await interaction.send(f"Pong! {int(self.bot.latency * 1000)}ms")

    # TODO
    @commands.slash_command(
    name="string_store",
    description="Stores the provided string in a variable only you can access",
    guild_ids=[SERVER_GUILD_ID]
    )
    async def string_store(self, interaction: ACI, string: str, name: str):
        await interaction.send(NOT_IMPLEMENTED)
        return

    # TODO
    @commands.slash_command(
        name="string_get",
        description="Retrieves the string associated to the variable",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def string_get(self, interaction: ACI, name: str):
        await interaction.send(NOT_IMPLEMENTED)

    @commands.slash_command(
        name="pfp",
        description="Returns the pfp of the selected user",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def pfp(self, interaction: ACI, user: Member):
        await interaction.send(user.avatar)

    @commands.slash_command(
        name="cmds",
        description="Lists available cmds",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def cmds(self, interaction: ACI):
        await interaction.response.send_message(CMDS)

    @commands.slash_command(
        name="spam_ping",
        description="Spam pings a user",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def spam_ping(self, interaction: ACI, user: Member, times: int):
        if not privileges.check_admin(interaction.user.id):
            await interaction.response.send_message(RESTRICTED)
            return
        
        for _ in range(0,times):
            await interaction.send(f"<@{user.id}>")


def setup(bot):
    bot.add_cog(Misc(bot))