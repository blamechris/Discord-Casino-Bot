import discord
from discord.ext import commands
import mysql.connector
import os
import random

# Enable default intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents) #initialize bot using '!' as prefix

# Connect to the MySQL server using environment variables
db = mysql.connector.connect(
    host=os.environ.get('DB_HOST', 'default_host'),  # Fallback to 'default_host' if not set
    user=os.environ.get('DB_USER', 'default_user'),  # Fallback to 'default_user' if not set
    password=os.environ.get('DB_PASSWORD', 'default_password'),  # Fallback to 'default_password' if not set
    database=os.environ.get('DB_NAME', 'default_database')  # Fallback to 'default_database' if not set
)
cursor = db.cursor(dictionary=True)

@bot.command()
async def createaccount(ctx):
    # Add user to the database
    query = "INSERT INTO users (discord_id, username) VALUES (%s, %s)"
    cursor.execute(query, (ctx.author.id, str(ctx.author)))
    db.commit()
    await ctx.send("Account created successfully!")

@bot.command()
async def mystats(ctx):
    query = "SELECT * FROM users WHERE discord_id = %s"
    cursor.execute(query, (ctx.author.id,))
    user_data = cursor.fetchone()
    
    if user_data:
        await ctx.send(f"Your stats: Chips: {user_data['chip_count']}")
    else:
        await ctx.send("You don't have an account. Please create one using !createaccount.")

suits = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
values = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']

deck = [(value, suit) for suit in suits for value in values]

def draw_card():
    card = random.choice(deck)  # Draw a random card from the deck
    deck.remove(card)  # Remove the drawn card from the deck
    return card

def shuffle_deck():
    random.shuffle(deck)  # Shuffle the deck

def eval_hand(hand_values):
    if sum(hand_values) > 21:
        return 'BUST'
    elif sum(hand_values) == 21:
        return 'BLACKJACK'
    else:
        return 'You have: {sum(hand_values)}, do you want to hit or stand?'


TOKEN = os.environ.get('BOT_TOKEN')

print(f"Bot token: {TOKEN}")  # Ensure you setup the token right

bot.run(TOKEN)  # Run the bot using the token provided