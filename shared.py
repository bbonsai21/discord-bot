from typing import Optional

SERVER_GUILD_ID = 1377655614003609630
RESTRICTED = "Restricted."
NOT_IMPLEMENTED = "Feature not implemented yet."
USER_NOT_CACHED = "User hasn't been cached - to start create a variable."
VAR_NOT_CACHED = "Variable hasn't been cached - to start create one."
SHAPES_NOT_EQUAL = "Matrices do not share the same shape."
MATRIX_NOT_SQUARE = "The provided matrix is not square."

COOLDOWN_TIME = 60
MAX_CACHE_SIZE = 100
cooldowns = {}  # {user_id: timestamp}

with open("./cmds.txt", "r") as f:
    CMDS = f.read()

# Formats an element to fit a certain Discord standard
def discord_format(elem: any, prev: Optional[str] = "", succ: Optional[str] = ""):
    return ("\u200b\n" + prev + "\n```\n" + str(elem) + "\n```\n" + succ)

