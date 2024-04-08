import discord
from discord.ext import commands
import mysql.connector
import os
import random
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()  # This loads the environment variables from .env

# Enable default intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents) #initialize bot using '!' as prefix

# Connect to the MySQL server using environment variables
# db = mysql.connector.connect(
#     host=os.environ.get('DB_HOST', 'default_host'),  # Fallback to 'default_host' if not set
#     user=os.environ.get('DB_USER', 'default_user'),  # Fallback to 'default_user' if not set
#     password=os.environ.get('DB_PASSWORD', 'default_password'),  # Fallback to 'default_password' if not set
#     database=os.environ.get('DB_NAME', 'default_database')  # Fallback to 'default_database' if not set
# )
# cursor = db.cursor(dictionary=True)

@bot.command()
async def createaccount(ctx):
    # Add user to the database
    # query = "INSERT INTO users (discord_id, username) VALUES (%s, %s)"
    # cursor.execute(query, (ctx.author.id, str(ctx.author)))
    # db.commit()
    await ctx.send("Account created successfully!")

@bot.command()
async def mystats(ctx):
    # query = "SELECT * FROM users WHERE discord_id = %s"
    # cursor.execute(query, (ctx.author.id,))
    # user_data = cursor.fetchone()
    
    # if user_data:
    #     await ctx.send(f"Your stats: Chips: {user_data['chip_count']}")
    # else:
    #     await ctx.send("You don't have an account. Please create one using !createaccount.")
    print("mystats")

@bot.command()
async def blackjack(ctx):
    shuffle_deck()  # Make sure the deck is shuffled before each game
    
    player_hand = [draw_card(), draw_card()]
    dealer_hand = [draw_card(), draw_card()]

    await ctx.send(f"Your hand: {player_hand[0]}, {player_hand[1]}. Do you want to 'hit' or 'stand'?")
    
    def check(m):
        return m.author == ctx.author and m.content.lower() in ["hit", "stand"]
    
    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)  # Wait for player's response
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you took too long to respond. Game over.")
        return

    while msg.content.lower() == "hit":
        player_hand.append(draw_card())
        player_value = calculate_hand_value(player_hand)
        if player_value > 21:
            await ctx.send(f"Card drawn: {player_hand[-1]}. Total: {player_value}. You busted!")
            return
        elif player_value == 21:
            await ctx.send(f"Card drawn: {player_hand[-1]}. Total: {player_value}. Blackjack!")
            break
        else:
            await ctx.send(f"Card drawn: {player_hand[-1]}. Total: {player_value}. Do you want to 'hit' or 'stand'?")
            try:
                msg = await bot.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.send("Sorry, you took too long to respond. Game over.")
                return

    # Dealer's turn to draw cards
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(draw_card())

    await end_game(ctx, player_hand, dealer_hand)

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

def calculate_hand_value(hand):
    """Calculate the value of a hand, taking Aces into account."""
    value = 0
    aces = 0
    for card in hand:
        if card[0] in ['Jack', 'Queen', 'King']:
            value += 10
        elif card[0] == 'Ace':
            aces += 1
            value += 11  # Initially count aces as 11
        else:
            value += int(card[0])
    
    # Adjust for aces if value goes over 21
    while value > 21 and aces:
        value -= 10  # Convert an ace from 11 to 1
        aces -= 1

    return value

async def end_game(ctx, player_hand, dealer_hand):
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)
    if player_value > 21:
        await ctx.send(f"You busted with a total of {player_value}. Dealer wins.")
    elif dealer_value > 21 or player_value > dealer_value:
        await ctx.send(f"You win! You had {player_value} and the dealer had {dealer_value}.")
    else:
        await ctx.send(f"Dealer wins with {dealer_value} against your {player_value}.")

TOKEN = os.environ.get('BOT_TOKEN')

print(f"Bot token: {TOKEN}")  # Ensure you setup the token right

bot.run(TOKEN)  # Run the bot using the token provided