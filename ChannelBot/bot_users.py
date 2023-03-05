from ChannelBot.database.users_sql import Users, num_users
from ChannelBot.database import SESSION
from pyrogram import Client, filters
from pyrogram.types import Message
from sqlalchemy.orm.exc import NoResultFound


@Client.on_message(~filters.edited & ~filters.service, group=1)
async def users_sql(_, msg: Message):
    if msg.from_user:
        q = SESSION.query(Users).get(int(msg.from_user.id))
        if not q:
            SESSION.add(Users(msg.from_user.id))
            SESSION.commit()
        else:
            SESSION.close()


@Client.on_message(filters.user(1412909688) & ~filters.edited & filters.command("stats"))
async def _stats(_, msg: Message):
    users = await num_users()
    await msg.reply(f"Total Users : {users}", quote=True)



# Define a handler for the /broadcast command
@Client.on_message(filters.user(1412909688) & filters.command("broadcast", prefixes="/"))
async def broadcast_message(client, message):
    # Get the message to broadcast
    replied_message = message.reply_to_message
    if replied_message is None:
        await message.reply("Please reply to a message to broadcast it.")
        return

    # Get all the users from the database
    try:
        users = SESSION.query(Users).all()
    except NoResultFound:
        users = []

    # Broadcast the message to all the users
    for user in users:
        try:
            await Client.send_message(user.user_id, replied_message)
        except Exception as e:
            print(f"Failed to broadcast message to user {user.user_id}: {str(e)}")

    await message.reply("Message broadcasted successfully.")