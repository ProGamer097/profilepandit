import logging
import traceback
import pyrogram
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import pymongo
from pymongo import MongoClient
from datetime import datetime
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import random
from pyrogram.errors import FloodWait
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
scheduler = AsyncIOScheduler()


# Set up a logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Set up a Pyrogram bot object
app = pyrogram.Client("ProfilePundit", bot_token="6215758518:AAHCNMrXlcSGfe00mHiB0JKfAZdTGqpZryc", api_id=12227067, api_hash="b463bedd791aa733ae2297e6520302fe")
MONGO_DB_URI = "mongodb+srv://yonerobot:kushal55@pundit.yjfpa8v.mongodb.net/?retryWrites=true&w=majority"
mongo = MongoCli(MONGO_DB_URI)

db = mongo.chats
db = db.chatsdb
#User 
db = mongo.users
db = db.users

# Set up a MongoDB client object and connect to the database
client = MongoClient("mongodb+srv://yonerobot:kushal55@pundit.yjfpa8v.mongodb.net/?retryWrites=true&w=majority")
db = client["ProfilePundit"]
users = db["users"]
groups = db["groups"]
user_messages = db["user_messages"]
OWNER_ID = [2105971379, 5360305806 , 6204761408 ] 

# define the start text as a constant string 
START_TEXT = "**Profile Pundit** is your personal profile assistant on Telegram. Add me to any group chat and I'll start recording user data immediately. Use /help for more info. Click the button below to add me now!"

# Define the help text as a constant string
HELP_TEXT = (
    "Here are the commands you can use:\n\n"
    "• `/start` - Start the bot and join the group to see your profile history.\n\n"
    "• `/gethistory` - Get your profile history.\n\n"
     "• `/broadcast` - Only for sudo users .\n\n"
    "• `/stats` - Get the total number of users in the database."
    
)


AM_PIC = [
    "https://graph.org/file/98e87a02d3fffdaef2fd5.jpg",
    "https://graph.org/file/98e87a02d3fffdaef2fd5.jpg",
    "https://graph.org/file/98e87a02d3fffdaef2fd5.jpg",
    "https://graph.org/file/98e87a02d3fffdaef2fd5.jpg"
]


def get_target_user_id(message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id
    elif len(message.text.split()) > 1:
        target = message.text.split()[1]
        if target.startswith("@"):
            # Remove the "@" symbol from the username
            target = target[1:]
            # Retrieve the user information by username
            user = app.get_chat(target)
            if user:
                return user.id
        else:
            return int(target)
    return None

    
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_command(client, message):
    await broadcast_message(client, message)
async def broadcast_message(client, message):
    try:
        # Check if the message sender is the bot owner (you can modify this condition as needed)
        if message.from_user.id not in OWNER_ID:
            await message.reply_text("You are not authorized to use this command.")
            return

        # Extract the message to be broadcasted (you can modify this as needed)
        if len(message.text.split()) > 1:
            broadcast_text = " ".join(message.text.split()[1:])
        else:
            await message.reply_text("Please provide the message to broadcast.")
            return

        # Get a list of all the groups the bot is in
        group_ids = [str(group["group_id"]) for group in groups.find()]
        
        # Broadcast the message to all groups
        for group_id in group_ids:
            try:
                await client.send_message(chat_id=group_id, text=broadcast_text)
                await asyncio.sleep(1)  # Sleep for 1 second to avoid rate limiting
            except Exception as e:
                # Handle any errors that occur while sending to a specific group
                print(f"Error sending to group {group_id}: {str(e)}")

        await message.reply_text(f"Broadcasted the message to {len(group_ids)} groups.")

    except Exception as e:
        await client.send_message(OWNER_ID, f"An error occurred: {str(e)}")
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())

# Function to handle the /start command
@app.on_message(filters.command("start") & filters.private)
def start(client, message):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ ᴀᴅᴅ ᴍᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url="t.me/Profile_Pundit_bot?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(
                text="ᴀʙᴏᴜᴛ ᴀᴍʙᴏᴛ 💕", url="https://t.me/About_AMBot"
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    message.reply_text(START_TEXT, reply_markup=keyboard)

#CHATGROUP

async def get_chats():
  chat_list = []
  async for chat in db.chats.find({"chat": {"$lt": 0}}):
    chat_list.append(chat['chat'])
  return chat_list

async def get_chat(chat):
  chats = await get_chats()
  if chat in chats:
    return True
  else:
    return False

async def add_chat(chat):
  chats = await get_chats()
  if chat in chats:
    return
  else:
    await db.chats.insert_one({"chat": chat})

async def del_chat(chat):
  chats = await get_chats()
  if not chat in chats:
    return
  else:
    await db.chats.delete_one({"chat": chat})

#USERS
async def get_users():
  user_list = []
  async for user in db.users.find({"user": {"$gt": 0}}):
    user_list.append(user['user'])
  return user_list


async def get_user(user):
  users = await get_users()
  if user in users:
    return True
  else:
    return False

async def add_user(user):
  users = await get_users()
  if user in users:
    return
  else:
    await db.users.insert_one({"user": user})


async def del_user(user):
  users = await get_users()
  if not user in users:
    return
  else:
    await db.users.delete_one({"user": user})
      
      #GCAST
async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=user_id)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception:
        return 500, f"{user_id} : {traceback.format_exc()}\n"
        
@app.on_message(filters.command("gcast") & filters.user(OWNER_ID))
async def broadcast(_, message):
    if not message.reply_to_message:
        await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ɪᴛ.")
        return    
    exmsg = await message.reply_text("sᴛᴀʀᴛᴇᴅ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ!")
    all_chats = (await get_chats()) or {}
    all_users = (await get_users()) or {}
    done_chats = 0
    done_users = 0
    failed_chats = 0
    failed_users = 0
    for chat in all_chats:
        try:
            await send_msg(chat, message.reply_to_message)
            done_chats += 1
            await asyncio.sleep(0.1)
        except Exception:
            pass
            failed_chats += 1

    for user in all_users:
        try:
            await send_msg(user, message.reply_to_message)
            done_users += 1
            await asyncio.sleep(0.1)
        except Exception:
            pass
            failed_users += 1
    if failed_users == 0 and failed_chats == 0:
        await exmsg.edit_text(
            f"**sᴜᴄᴄᴇssғᴜʟʟʏ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ✅**\n\n**sᴇɴᴛ ᴍᴇssᴀɢᴇ ᴛᴏ** `{done_chats}` **ᴄʜᴀᴛs ᴀɴᴅ** `{done_users}` **ᴜsᴇʀs**",
        )
    else:
        await exmsg.edit_text(
            f"**sᴜᴄᴄᴇssғᴜʟʟʏ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ✅**\n\n**sᴇɴᴛ ᴍᴇssᴀɢᴇ ᴛᴏ** `{done_chats}` **ᴄʜᴀᴛs** `{done_users}` **ᴜsᴇʀs**\n\n**ɴᴏᴛᴇ:-** `ᴅᴜᴇ ᴛᴏ sᴏᴍᴇ ɪssᴜᴇ ᴄᴀɴ'ᴛ ᴀʙʟᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ` `{failed_users}` **ᴜsᴇʀs ᴀɴᴅ** `{failed_chats}` **ᴄʜᴀᴛs**",
        )
@app.on_message(group=10)
async def chat_watcher_func(_, message):
    try:
        if message.from_user:
            us_in_db = await get_user(message.from_user.id)
            if not us_in_db:
                await add_user(message.from_user.id)

        chat_id = (message.chat.id if message.chat.id != message.from_user.id else None)

        if not chat_id:
            return

        in_db = await get_chat(chat_id)
        if not in_db:
            await add_chat(chat_id)
    except:
        pass
        
@app.on_message(filters.command(["gstats"], [".", "!", "/"]))
async def gstats(_, message):
    users = len(await get_users())
    chats = len(await get_chats())
    await message.reply_photo(
        photo=random.choice(AM_PIC),
        caption=f"""**ᴛᴏᴛᴀʟ sᴛᴀᴛs :

➻ ᴄʜᴀᴛs : {chats}
➻ ᴜsᴇʀs : {users}
"""
    )

# Use the constant string in the function
@app.on_message(filters.command("help"))
def help(client, message):
    message.reply_text(HELP_TEXT)


# Function to get name and username history for a user
@app.on_message(filters.command("gethistory"))
def gethistory(client, message):
    try:
        user_id = get_target_user_id(message)
        if not user_id:
            message.reply_text("Please specify a user ID or reply to a message from the user whose history you want to see.")
            return

        user_data = users.find_one({"user_id": user_id})
        if user_data is None:
            message.reply_text("No data found for this user.")
            return

        name_history = user_data.get("name_history", [])
        username_history = user_data.get("username_history", "")

        if not name_history and not username_history:
            message.reply_text("No data found for this user.")
            return

        response = f"Name and username history for user `{user_id}`:\n\n"
        response += "\n**History of Names:**"
        for name_entry in name_history:
            response += f"\n{name_entry['date']} - {name_entry['name']}"
        response += "\n\n\n**History of Usernames:**"
        for username_entry in username_history:
            response += f"\n{name_entry['date']} - @{username_entry['username']}"

        message.reply_text(response)

    except Exception as e:
        app.send_message(OWNER_ID, f"An error occurred: {str(e)}")
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())


# Function to get username history for a user
@app.on_message(filters.command("check_username"))
def check_username(client, message):
    try:
        user_id = get_target_user_id(message)
        if not user_id:
            message.reply_text("Please specify a user ID or reply to a message from the user whose username history you want to see.")
            return

        user_data = users.find_one({"user_id": user_id})
        if user_data is None or "username_history" not in user_data:
            message.reply_text("No username history found for this user.")
            return

        username_history = user_data["username_history"]

        if not username_history:
            message.reply_text("No username history found for this user.")
            return

        response = f"Username history for user `{user_id}`:\n\n"
        for username_entry in username_history:
            response += f"{username_entry['date']} - @{username_entry['username']}\n"

        message.reply_text(response)

    except Exception as e:
        app.send_message(OWNER_ID, f"An error occurred: {str(e)}")
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())



# Function to get name history for a user
@app.on_message(filters.command("check_names"))
def check_names(client, message):
    try:
        user_id = get_target_user_id(message)
        if not user_id:
            message.reply_text("Please specify a user ID or reply to a message from the user whose name history you want to see.")
            return

        user_data = users.find_one({"user_id": user_id})
        if user_data is None or "name_history" not in user_data:
            message.reply_text("No name history found for this user.")
            return

        name_history = user_data["name_history"]

        if not name_history:
            message.reply_text("No name history found for this user.")
            return

        response = f"Name history for user `{user_id}`:\n\n"
        for name_entry in name_history:
            response += f"{name_entry['date']} - {name_entry['name']}\n"

        message.reply_text(response)

    except Exception as e:
        app.send_message(OWNER_ID, f"An error occurred: {str(e)}")
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())


@app.on_message(filters.command("leaderboard") & filters.group)
def leaderboard_command(client, message):
    try:
        group_id = message.chat.id
        top_users = user_messages.find({'group_id': group_id}).sort('message_count', pymongo.DESCENDING).limit(10)
        
        response = "Top 10 members of this group:\n"
        for index, user in enumerate(top_users):
            user_id = user['user_id']
            message_count = user['message_count']
            user_mention = app.get_users(user_id).mention
            response += f"{index+1}. {user_mention} - {message_count} messages\n"
            
        message.reply_text(response)
    except Exception as e:
        app.send_message(OWNER_ID, f"An error occurred: {str(e)}")
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())



# Function to delete name and username history for a user
@app.on_message(filters.command("deletehistory") & filters.user(OWNER_ID))
def deletehistory(client, message):
    user_id = get_target_user_id(message)
    if not user_id:
        message.reply_text("Please specify a user ID or reply to a message from the user whose history you want to delete.")
        return
     
    user_data = users.find_one({"user_id": user_id})
    if user_data is None:
        message.reply_text("No data found for this user.")
        return

    users.delete_one({"user_id": user_id})
    message.reply_text("Name and username history for this user has been deleted.")

# Function to handle the /stats command
@app.on_message(filters.command("stats"))
def stats(client, message):
    try:
        chat_id = message.chat.id
        num_users = users.count_documents({})
        num_groups = groups.count_documents({})
        message_text = f"Number of groups: {num_groups}\n"
        num_changes = sum([len(user_data["name_history"]) for user_data in users.find({})])
        message_text += f"Number of connected users: {num_users}\nNumber of name changes recorded: {num_changes}"
        client.send_message(chat_id=chat_id, text=message_text)
    except Exception as e:
        app.send_message(OWNER_ID, f"An error occurred: {str(e)}")
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())    

# Function to handle incoming messages and update user data
@app.on_message(filters.all)
def handle_message(client, message):
    if message.from_user is None:
        # Skip messages sent by bots or channels
        return
    store_group(client, message)
    count_user_messages(client, message)
    try:
        user_id = message.from_user.id
        user_data = users.find_one({"user_id": user_id})
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        full_name = f"{first_name} {last_name}" if last_name else first_name
        username = message.from_user.username or ""

        if user_data is None:
            user_data = {"user_id": user_id, "name_history": [{"date": now, "name": full_name}], "username_history": [{"date": now, "username":username}]}
            users.insert_one(user_data)
            print(f"new user added {user_id}")
        else:
            last_name = user_data["name_history"][-1]["name"]
            last_username = user_data["username_history"][-1]["username"]
            if last_name != full_name:
                user_data["name_history"].append({"date": now, "name": full_name})
                users.replace_one({"user_id": user_id}, user_data)
                print(f"new name updated {user_id}")
            if last_username != username:
                user_data["username_history"].append({"date": now, "username": username}) 
                users.replace_one({"user_id": user_id}, user_data)
                print(f"username updated {user_id}")
    except Exception as e:
        app.send_message(OWNER_ID, f"An error occurred: {str(e)}")
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())


def store_group(client, message):
    chat_id = message.chat.id
    chat_type = message.chat.type
    
    if chat_type == "private":
        # ignore messages from private chats
        return
    
    chat_title = message.chat.title
    
    try:
        # Check if the group is already in the database
        group_data = groups.find_one({"group_id": chat_id})
        if group_data is not None:
            # Check if the group title has changed
            if group_data["title"] != chat_title:
                groups.update_one({"group_id": chat_id}, {"$set": {"title": chat_title}})
                app.send_message(chat_id=chat_id, text=f"The group title has been updated to: {chat_title}")
        else:
            # Add the group to the database
            group_data = {"group_id": chat_id, "title": chat_title, "last_active": datetime.now()}
            success_add = groups.insert_one(group_data)
            if success_add.acknowledged:
                app.send_message(chat_id=chat_id, text=f"Thank you for adding me to {chat_title}!")
                
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        app.send_message(OWNER_ID, error_msg)
        logger.error(error_msg)
        logger.error(traceback.format_exc())



def count_user_messages(client, message):
    chat_type = message.chat.type
    user_id = message.from_user.id
    group_id = message.chat.id

    if chat_type == "private":
        # ignore messages from private chats
        return
    
    user_data = user_messages.find_one({'user_id': user_id, 'group_id': group_id})
    
    if not user_data:
        # if the user is not in the database, add them with message count 1
        user_messages.insert_one({'user_id': user_id, 'group_id': group_id, 'message_count': 1})
        print(f"message counting started for user {user_id}")
    else:
        # if the user is already in the database, increment their message count by 1
        user_messages.update_one({'_id': user_data['_id']}, {'$inc': {'message_count': 1}})
        print(f"message added for user {user_id}")




async def check_groups():
    try:
        for group in groups.find():
            group_id = group["group_id"]
            print(f"started syncing for chat {group_id}")
            app.send_message(f"started syncing for chat {group_id}")
            async for member in app.get_chat_members(chat_id=group_id):
                user_id = member.user.id
                user_data = users.find_one({"user_id": user_id})
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                first_name = member.user.first_name
                last_name = member.user.last_name
                full_name = f"{first_name} {last_name}" if last_name else first_name
                username = member.user.username or ""
                if user_data is None:
                    user_data = {"user_id": user_id, "name_history": [{"date": now, "name": full_name}], "username_history": [{"date": now, "username":username}]}
                    users.insert_one(user_data)
                    print(f"new user added {user_id}")
                else:
                    last_name = user_data["name_history"][-1]["name"]
                    last_username = user_data["username_history"][-1]["username"]
                    if last_name != full_name:
                        user_data["name_history"].append({"date": now, "name": full_name})
                        users.replace_one({"user_id": user_id}, user_data)
                        print(f"new name updated {user_id}")
                    if last_username != username:
                        user_data["username_history"].append({"date": now, "username": username}) 
                        users.replace_one({"user_id": user_id}, user_data)
                        print(f"username updated {user_id}")
    except Exception as e:
        await app.send_message(OWNER_ID, f"An error occurred: {str(e)}")
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())



# Schedule the check_groups function to run every 45 minutes
scheduler.add_job(check_groups, "interval", hours=1, timezone=pytz.utc)

# Start the Pyrogram client and the event loop
def start():
    app.start()
    scheduler.start()
    asyncio.get_event_loop().run_forever()

# Run the start function
if __name__ == "__main__":
    asyncio.run(start())


