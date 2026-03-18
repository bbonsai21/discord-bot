import os
from typing import Optional
import time

import privileges
from disnake.ext import commands
from disnake import Member, File
from disnake import ApplicationCommandInteraction as ACI

from shared import discord_format, SERVER_GUILD_ID, RESTRICTED, NOT_IMPLEMENTED, COOLDOWN_TIME
from shared import USER_NOT_CACHED, VAR_NOT_CACHED, SHAPES_NOT_EQUAL, MATRIX_NOT_SQUARE, cooldowns

import sympy as smp
import numpy as np
from matplotlib import pyplot as plt

MAX_USERS_CACHE = 50 # max users
MAX_VARS_CACHE = 10 # max variables
DATA_CACHE = {} # format: {"user_id": {"variable1": value1, "variable2": value2, ...}, ...}

dx = 0.1
PLOT_COOLDOWN_TIME = 5

# Checks whether it's possible to insert data in DATA_CACHE[user_id][name]. If yes, it does.
async def insert_data(interaction, name: str, data: any):
    msg = ""
    user_id = interaction.user.id

    if name:
        if (user_id in DATA_CACHE):
            if (name in DATA_CACHE[user_id]):
                msg = msg + f"**Overwritten `{name}`**\n"
                DATA_CACHE[user_id][name] = data
                return True, msg

            if (len(DATA_CACHE[user_id]) >= MAX_VARS_CACHE):
                await interaction.send(f"Maximum amount of variables reached ({MAX_VARS_CACHE}). Use `/free()` to delete some.\n")
                return False, msg
            
            DATA_CACHE[user_id][name] = data
        else:
            if (len(DATA_CACHE) >= MAX_USERS_CACHE):
                await interaction.send(f"Maximum amount of users reached ({MAX_USERS_CACHE}). Either wait for someone to `/free` or for the system to free someone.\n")
                return False, msg
            
            DATA_CACHE[user_id] = {}
            DATA_CACHE[user_id][name] = data

    return True, msg

class Math(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="rand_matrix",
        description="Generates a matrix with random floating-point elements in the range (0, 1]",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def rand_matrix(self, interaction: ACI, rows: int, cols: int, name: Optional[str] = None):
        if (rows > 10 or rows <= 0 or cols > 10 or cols <= 0):
            await interaction.send("`rows` and `cols` must be integers in the range (0, 10]")

        arr = np.random.random(size=(int(rows), int(cols)))

        success, msg = await insert_data(interaction, name, arr)
        if not success:
            return

        await interaction.send(msg + discord_format(arr))

    @commands.slash_command(
        name="randint_matrix",
        description="Generates a matrix with random integer elements in the provided range",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def randint_matrix(self, interaction: ACI, rows: int, cols: int, min: int, max: int, name: Optional[str] = None):
        if (rows > 10 or rows <= 0 or cols > 10 or cols <= 0):
            await interaction.send("`rows` and `cols` must be integers in the range (0,10].")

        arr = np.random.randint(int(min), int(max), size=(int(rows), (cols)))
        
        success, msg = await insert_data(interaction, name, arr)
        if not success:
            return

        await interaction.send(msg + discord_format(arr))

    @commands.slash_command(
        name="printall",
        description="Prints every active data position",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def printall(self, interaction: ACI):
        user_id = interaction.user.id

        if (not privileges.check_admin(user_id)):
            await interaction.send(RESTRICTED)
        else:
            await interaction.send(discord_format(DATA_CACHE))

    @commands.slash_command(
        name="printuser",
        description="Prints every active data position",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def printuser(self, interaction: ACI, user: Member):
        if (not privileges.check_admin(user.id)):
            await interaction.send(RESTRICTED)
            return
        
        if (int(user.id) in DATA_CACHE):
            await interaction.send(discord_format(DATA_CACHE[int(user)]))
        else:
            await interaction.send("Empty.")

    @commands.slash_command(
        name="free",
        description="Free your position in the data cache",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def free(self, interaction: ACI):
        if (interaction.user.id in DATA_CACHE):
            DATA_CACHE.pop(interaction.user.id)
            await interaction.send("Cache free'd.")
            return
        else:
            await interaction.send("Nothing to free.")

    @commands.slash_command(
        name="delete",
        description="Delete  one of your variables in the data cache",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def delete(self, interaction: ACI, var_name: str):
        user_id = interaction.user.id
        
        if user_id in DATA_CACHE and var_name in DATA_CACHE[user_id]:
            DATA_CACHE[user_id].pop(var_name)
            await interaction.send(f"Deleted {var_name}.")
        else:
            await interaction.send("Nothing to delete.")

    @commands.slash_command(
        name="matrix_add",
        description="Sum 2 matrices",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def matrixAdd(self, interaction: ACI, first: str, second: str, name: Optional[str] = None): 
        user_id = interaction.user.id
        
        if (user_id not in DATA_CACHE):
            await interaction.send(USER_NOT_CACHED)
            return

        if (first not in DATA_CACHE[user_id]):
            await interaction.send(VAR_NOT_CACHED + f" ({first})")
            return
        
        if (second not in DATA_CACHE[user_id]):
            await interaction.send(VAR_NOT_CACHED + f" ({second})")
            return
        
        arr1 = DATA_CACHE[user_id][first]
        arr2 = DATA_CACHE[user_id][second]

        if (arr1.shape != arr2.shape):
            await interaction.send(SHAPES_NOT_EQUAL)
            return
        
        result = arr1+arr2
        success, msg = await insert_data(interaction, name, result)
        if (not success):
            return
        
        await interaction.send(msg + discord_format(result))

    @commands.slash_command(
        name="matrix_sub",
        description="Sub 2 matrices",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def matrixSub(self, interaction: ACI, first: str, second: str, name: Optional[str] = None): 
        user_id = interaction.user.id
        
        if (user_id not in DATA_CACHE):
            await interaction.send(USER_NOT_CACHED)
            return

        if (first not in DATA_CACHE[user_id]):
            await interaction.send(VAR_NOT_CACHED + f" ({first})")
            return
        
        if (second not in DATA_CACHE[user_id]):
            await interaction.send(VAR_NOT_CACHED + f" ({second})")
            return
        
        arr1 = DATA_CACHE[user_id][first]
        arr2 = DATA_CACHE[user_id][second]

        if (arr1.shape != arr2.shape):
            await interaction.send(SHAPES_NOT_EQUAL)
            return
        
        result = arr1-arr2
        success, msg = await insert_data(interaction, name, result)
        if (not success):
            return
        
        await interaction.send(msg + discord_format(result))

    @commands.slash_command(
        name="matrix_transpose",
        description="Transpose a matrix",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def matrixT(self, interaction: ACI, matrix: str, name: Optional[str] = None):
        user_id = interaction.user.id

        if (user_id not in DATA_CACHE or matrix not in DATA_CACHE[user_id]):
            await interaction.send(VAR_NOT_CACHED)
            return
        
        arr = DATA_CACHE[user_id][matrix]
        
        transposed = arr.T
        success, msg = await insert_data(interaction, name, transposed)
        if (not success):
            return

        await interaction.send(msg + discord_format(transposed))

    @commands.slash_command(
        name="matrix_det",
        description="Calculate the determinant of a matrix",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def matrixDet(self, interaction: ACI, matrix: str):
        user_id = interaction.user.id

        if (user_id not in DATA_CACHE or matrix not in DATA_CACHE[user_id]):
            await interaction.send(VAR_NOT_CACHED)
            return
        
        arr = DATA_CACHE[user_id][matrix]
        if (arr.shape[0] != arr.shape[1]):
            await interaction.send(MATRIX_NOT_SQUARE)
            return
        
        if (arr.dtype == int):
            await interaction.send(discord_format(int(np.linalg.det(arr))))
        else:
            await interaction.send(discord_format(np.linalg.det(arr)))

    @commands.slash_command(
        name="matrix_eigen",
        description="Calculate the determinant of a matrix",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def matrixEigen(self, interaction: ACI, matrix: str):
        user_id = interaction.user.id

        if (user_id not in DATA_CACHE or matrix not in DATA_CACHE[user_id]):
            await interaction.send(VAR_NOT_CACHED)
            return
        
        result = np.linalg.eig(DATA_CACHE[user_id][matrix])
        await interaction.send(discord_format(getattr(result, "eigenvalues"), "Eigenvalues:\n") + discord_format(getattr(result, "eigenvectors"), "Eigenvectors:\n"))

    # TODO!
    @commands.slash_command(
        name="matrix_solve",
        description="Solve the equation ax = b, for the matrix x",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def matrix_solve(self, interaction: ACI, matrix: str):
        await interaction.send(NOT_IMPLEMENTED)

    # SYMPY SYMBOLIC CALCULATIONS
    @commands.slash_command(
        name="expr",
        description="Simplifies an expression in the given variables",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def expr(self, interaction: ACI, expression: str, variables: Optional[str] = "x", name: Optional[str] = None, latex: Optional[bool] = False):
        syms = smp.symbols(variables.replace(",", " "))
        if isinstance(syms, smp.Symbol):
            syms = (syms,)

        try:
            expr = smp.sympify(expression, locals={v.name: v for v in syms})
            simplified = smp.simplify(expr)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")
            return

        if latex:
            result = f"latex\n{smp.latex(simplified)}"
        else:
            result = f"`{simplified}`"

        await interaction.response.send_message(discord_format(result))  

    # MATPLOTLIB
    @commands.slash_command(
        name="plot_matrix",
        description="Plots a matrix",
        guild_ids=[SERVER_GUILD_ID]
    )
    async def plotMatrix(self, interaction: ACI, var: str):
        user_id = interaction.user.id

        if (user_id not in DATA_CACHE or var not in DATA_CACHE[user_id]):
            await interaction.send("You first need to create a matrix.")
            return
        
        if user_id not in privileges.admins:
            if user_id in cooldowns:
                elapsed = time.time() - cooldowns[user_id]
                if elapsed < COOLDOWN_TIME:
                    await interaction.followup.send(
                        f"Cooldown active. Wait {int(COOLDOWN_TIME - elapsed)}s"
                    )
                    return
            cooldowns[user_id] = time.time()

        if (os.path.exists("./plots/" + str(user_id) + ".png")):
            os.remove("./plots/" + str(user_id) + ".png")

        await interaction.response.defer()

        arr = DATA_CACHE[user_id][var]

        plt.plot(*arr)
        path = "./plots/" + str(user_id) + ".png"
        plt.savefig(path, dpi=300, bbox_inches="tight")
        plt.close()

        await interaction.followup.send(file=File(path))


def setup(bot):
    bot.add_cog(Math(bot))