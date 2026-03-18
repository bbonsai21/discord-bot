import privileges
from disnake.ext import commands
from disnake import FFmpegPCMAudio
from disnake import ApplicationCommandInteraction as ACI

from shared import SERVER_GUILD_ID

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
    name="vc_connect",
    description="Connects to your voice channel",
    guild_ids=[SERVER_GUILD_ID]
    )
    async def vc_connect(interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("Join a voice channel first.")
            return

        vc = await interaction.user.voice.channel.connect()
        vc.play(FFmpegPCMAudio("/home/doppelblitz/Desktop/Ghost.mp3"))

    

def setup(bot):
    bot.add_cog(Voice(bot))