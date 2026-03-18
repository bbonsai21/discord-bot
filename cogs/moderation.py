import privileges
from disnake.ext import commands
from disnake import Member, Embed, Color
from shared import discord_format, SERVER_GUILD_ID, RESTRICTED
from disnake import ApplicationCommandInteraction as ACI

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="info",
        description="Returns infos about a user",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def info(self, interaction: ACI, user: Member):
        if not privileges.check_admin(interaction.user.id):
            await interaction.response.send_message(RESTRICTED)
            return

        embed = Embed(
            title=f"**{user.name}**",
            color=Color.blurple()
        )

        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
            
        embed.add_field(name="Creation date", value=user.created_at.strftime("%d/%m/%Y %H:%M"), inline=True)
        embed.add_field(name="Join date", value=user.joined_at.strftime("%d/%m/%Y %H:%M"), inline=True)
        embed.add_field(name="Top role", value=user.top_role.mention, inline=True)
        embed.add_field(name="Mutual servers", value=", ".join([g.name for g in user.mutual_guilds]) or "None", inline=True)
        embed.add_field(name="On mobile", value=str(user.is_on_mobile()), inline=True)

        await interaction.response.send_message(embed=embed)

    @commands.slash_command(
        name="add_mod",
        description="Adds a moderator to the bot",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def add_mod(self, interaction: ACI, user: Member):
        if not privileges.check_admin(interaction.user.id):
            await interaction.response.send_message(RESTRICTED)
            return
        
        privileges.add_admin(int(user.id))
        await interaction.response.send_message(f"Added <@{user.id}> as bot privileged user.")

    @commands.slash_command(
        name="remove_mod",
        description="Removes a moderator from the bot",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def remove_mod(self, interaction: ACI, user: Member):
        if not privileges.check_admin(interaction.user.id):
            await interaction.response.send_message(RESTRICTED)
            return
        
        if privileges.remove_admin(user.id):
            await interaction.response.send_message(f"Added <@{user.id}> as bot privileged user.")
        else:
            await interaction.response.send_message(f"{user.name} is not a mod.")

    @commands.slash_command(
        name="print_admins",
        description="Prints all admins",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def print_admins(self, interaction: ACI):    
        admins = privileges.get_admins()
        admins_str = ", ".join(str(uid) for uid in admins)

        await interaction.response.send_message(discord_format(admins_str))

    @commands.slash_command(
        name="print_id",
        description="Prints the unique ID of the specified user",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def print_id(self, interaction: ACI, user: Member):
        await interaction.response.send_message(user.id)

def setup(bot):
    bot.add_cog(Moderation(bot))