import discord
from discord.ext import commands
from pymongo import MongoClient
import os

# Enable default intents
intents = discord.Intents.default()

# If your bot needs to track presences or members, you can enable those intents specifically (be mindful of the privacy implications and the need to enable these in the Discord Developer Portal as well):
# intents.presences = True
# intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents) #initialize bot using '!' as prefix

# Connect to the MongoDB server running on localhost
client = MongoClient('mongodb://localhost:27017/')

# Access the 'discord_bot_db' database
db = client['discord_bot_db']

@bot.command()
async def createaccount(ctx):
    # Add user to the database
    db.users.insert_one({"discord_id": ctx.author.id, "username": str(ctx.author)})
    await ctx.send("Account created successfully!")

@bot.command()
async def mystats(ctx):
    """
    A command that retrieves and displays the user's stats.

    Parameters:
    - ctx: The context object representing the invocation context of the command.

    Returns:
    - None

    Raises:
    - None
    """
    # Retrieve user stats from the database
    user_data = db.users.find_one({"discord_id": ctx.author.id})

    if user_data:
        # If user data exists, send a message with the user's chip count
        await ctx.send(f"Your stats: Chips: {user_data['chip_count']}")
    else:
        # If user data doesn't exist, send a message to create an account
        await ctx.send("You don't have an account. Please create one using !createaccount.")

TOKEN = os.environ.get('BOT_TOKEN')

print(f"Bot token: {TOKEN}")  # Add this line

bot.run(TOKEN)  # Run the bot using the token provided