with open("privileges.txt", "r") as f:
    admins = {int(line.strip()) for line in f}

def check_admin(user_id):
    return user_id in admins

def add_admin(user_id):
    if user_id not in admins:
        admins.add(user_id)
        with open("privileges.txt", "a") as f:
            f.write(f"{user_id}\n")

def remove_admin(user_id):
    if user_id not in admins:
        return False
    
    admins.remove(user_id)
    with open("privileges.txt", "w") as f:
        for uid in admins:
            f.write(f"{uid}\n")
            
    return True

def get_admins():
    return admins.copy()