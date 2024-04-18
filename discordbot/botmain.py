import discord
from discord.ext import commands
import mysql.connector
import os
import random
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime, timedelta
from card_images import card_mapping

from database import *

load_dotenv()  # This loads the environment variables from .env

# Enable default intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents) #initialize bot using '!' as prefix

# Connect to the MySQL server using environment variables
db = database()


@bot.command(help="Create an account to start playing games and rank.")
async def createaccount(ctx):
    # Add user to the database
    db.create_account(ctx.author.id, ctx.author.name)
    print("createaccount called")


@bot.command(help="Displays your current stats, username, and your rank based on the account creation order (Will update to track highscore stuff).")
async def mystats(ctx):
    user_data = db.get_player_stats(ctx.author.id)
    if not user_data:
        await ctx.send("You don't have an account. Please create one using !createaccount.")
        return
    
    wins = user_data['wins']
    losses = user_data['losses']
    total_games = wins + losses
    win_percentage = (wins / total_games * 100) if total_games > 0 else 0

    last_withdrawal = user_data['last_withdrawal']
    last_withdrawal_str = last_withdrawal.strftime("%Y-%m-%d %H:%M:%S") if last_withdrawal else "Never"
    # With an embed like this
    embed = discord.Embed(title="Your Stats", color=discord.Color.green())
    embed.add_field(name="Username", value=ctx.author, inline=True)
    embed.add_field(name="Chips", value=user_data['chip_count'], inline=True)
    embed.add_field(name="Wins", value=wins, inline=True)
    embed.add_field(name="Losses", value=losses, inline=True)
    embed.add_field(name="Total games played", value=total_games, inline=True)
    embed.add_field(name="Win percentage", value=f"{win_percentage:.2f}%", inline=True)
    embed.add_field(name="Last withdrawal", value=last_withdrawal_str, inline=True)
    await ctx.send(embed=embed)

    print("mystats called")


@bot.command(help="Displays the leaderboard. Choose W for wins, L for losses, T for total games, or C for chip count.")
async def leaderboard(ctx):
    # Prompt user for the type of leaderboard they want to see
    leaderboard_message = ("Please choose a leaderboard:\n"
                           "`W` - Top 5 by Wins\n"
                           "`L` - Top 5 by Losses\n"
                           "`T` - Top 5 by Total Games Played\n"
                           "`C` - Top 5 by Chip Count")
    await ctx.send(leaderboard_message)

    # Check function to ensure the response is from the same user and in the same channel
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.upper() in ['W', 'L', 'T', 'C']

    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)  # 30 seconds to reply
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond.")
        return

    # Query based on user input
    selection = msg.content.upper()
    if selection == 'W':
        query = """
        SELECT username, wins FROM users ORDER BY wins DESC LIMIT 5
        """
    elif selection == 'L':
        query = """
        SELECT username, losses FROM users ORDER BY losses DESC LIMIT 5
        """
    elif selection == 'T':
        query = """
        SELECT username, (wins + losses) AS total_games FROM users ORDER BY total_games DESC LIMIT 5
        """
    elif selection == 'C':
        query = """
        SELECT username, chip_count FROM users ORDER BY chip_count DESC LIMIT 5
        """

    # Execute the query and fetch results
    db.cursor.execute(query)
    results = db.cursor.fetchall()
    if not results:
        await ctx.send("No data found for the selected category.")
        return

    # Format and send the leaderboard
    leaderboard_title = f"Top 5 Players by {'Wins' if selection == 'W' else 'Losses' if selection == 'L' else 'Total Games' if selection == 'T' else 'Chip Count'}"
    leaderboard_content = "\n".join([f"{idx + 1}. {result['username']} - {result[list(result.keys())[1]]}" for idx, result in enumerate(results)])
    
    embed = discord.Embed(title=leaderboard_title, color=discord.Color.blue())
    embed.add_field(name="Players", value=leaderboard_content, inline=False)

    # Send the embed
    await ctx.send(embed=embed)
    print("leaderboard called")


@bot.command(help="Withdraw 1000 chips once every hour.")
async def withdraw(ctx):
    current_time = datetime.utcnow()
    user_id = ctx.author.id

    if not db.get_player_stats(user_id):
        await ctx.send("You don't have an account. Please create one using !createaccount.")
        return
    can_withdraw = can_user_withdraw(user_id)

    if can_withdraw:
        # Update chip count and last withdrawal timestamp
        db.deposit(user_id, 1000)
        db.update_last_withdraw(user_id, current_time)
        await ctx.send("You have successfully withdrawn 1000 chips!")
    else:
        # Calculate time remaining until the next possible withdrawal
        time_remaining = timedelta(hours=1) - (current_time - db.get_last_withdraw(user_id))
        minutes, seconds = divmod(time_remaining.seconds, 60)
        await ctx.send(f"You must wait {minutes} minutes and {seconds} seconds before you can withdraw again.")
    print("withdraw called")

def can_user_withdraw(discord_id):
    current_time = datetime.utcnow()
    last_withdrawal = db.get_last_withdraw(discord_id)
    return (last_withdrawal is None or current_time - last_withdrawal >= timedelta(hours=1))


@bot.command(help="Shows the card images for a game of blackjack.")
async def showcards(ctx, *, card_name: str):
    # Assuming the card name is exactly as it appears in the dictionary
    if card_name in card_mapping:
        embed = discord.Embed(title=f"Here is your {card_name}", color=discord.Color.blue())
        #embed.set_image(url=card_mapping[card_name])
        await ctx.send(embed=embed)
    else:
        await ctx.send("Card not found. Please make sure the card name is correct.")


@bot.command(help="Starts a game of blackjack. You must wager some of your chips.")
async def blackjack(ctx, wager: int = 0):
    # Check if the wager was provided
    if wager is None:
        await ctx.send("Please include a wager amount with the command. Example: `!blackjack 50`")
        return

    # Check if the wager is a valid number
    if wager <= 0:
        await ctx.send("Your wager must be a positive number.")
        return

    # Check if the user has an account and sufficient chips
    result = db.get_player_stats(ctx.author.id)
    
    if not result:
        await ctx.send("You don't have an account. Please create one using !createaccount.")
        return

    if result['chip_count'] < wager or wager <= 0:
        await ctx.send("You do not have enough chips or your wager is invalid.")
        return

    # Start the game
    shuffle_deck()
    player_hand = [draw_card(), draw_card()]
    dealer_hand = [draw_card(), draw_card()]

    await show_hands(ctx, player_hand, dealer_hand, initial=True)

    # Player's turn
    player_value = calculate_hand_value(player_hand)
    if player_value == 21:
        await end_game(ctx, player_hand, dealer_hand, wager)
        return

    while True:
        choice = await ctx.send(f"Your hand: {', '.join(map(str, player_hand))} ({player_value}). Do you want to 'hit' or 'stand'?")
        msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.content.lower() in ['hit', 'stand'])

        if msg.content.lower() == 'stand':
            break

        if msg.content.lower() == 'hit':
            player_hand.append(draw_card())
            player_value = calculate_hand_value(player_hand)
            if player_value > 21:
                await ctx.send(f"You drew {player_hand[-1]}, and now have a total of {player_value}. You busted!")
                db.blackjack_result("LOSS", ctx.author.id, -wager)
                return
            elif player_value == 21:
                await ctx.send(f"You drew {player_hand[-1]}, and now have a total of {player_value}.")
                break

    # Dealer's turn
    dealer_value = calculate_hand_value(dealer_hand)
    while dealer_value < 17:
        dealer_hand.append(draw_card())
        dealer_value = calculate_hand_value(dealer_hand)

    await show_hands(ctx, player_hand, dealer_hand, initial=False)
    await end_game(ctx, player_hand, dealer_hand, wager)
    print("blackjack called")

async def show_hands(ctx, player_hand, dealer_hand, initial=False):
    if initial:
        dealer_display = f"{dealer_hand[0]}, Hidden"
    else:
        dealer_display = ', '.join(map(str, dealer_hand))
    player_display = ', '.join(map(str, player_hand))
    await ctx.send(f"Dealer's hand: {dealer_display}\nYour hand: {player_display}")

async def end_game(ctx, player_hand, dealer_hand, wager):
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)
    result_message = ""

    if player_value > 21:
        result_message = f"You busted with a total of {player_value}. Dealer wins."
        db.blackjack_result("LOSS", ctx.author.id, -wager)
    elif dealer_value > 21 or player_value > dealer_value:
        if player_value == 21 and len(player_hand) == 2:  # Check for a blackjack
            win_amount = int(1.5 * wager)
            result_message = f"Blackjack! You win {win_amount} chips!"
            db.blackjack_result("WIN", ctx.author.id, win_amount)
        else:
            result_message = f"You win! You had {player_value} and the dealer had {dealer_value}. You win {wager * 2} chips!"
            db.blackjack_result("WIN", ctx.author.id, wager*2)
    else:
        result_message = f"Dealer wins with {dealer_value} against your {player_value}."
        db.blackjack_result("LOSS", ctx.author.id, -wager)
    await ctx.send(result_message)

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

async def end_game(ctx, player_hand, dealer_hand, wager):
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)
    user_id = ctx.author.id

    if player_value > 21 or (dealer_value <= 21 and dealer_value > player_value):
        result_message = "You lost!"
        update_stats = "UPDATE users SET losses = losses + 1, chip_count = chip_count - %s WHERE discord_id = %s"
        # update_values = (-wager, user_id)
        db.blackjack_result("LOSS", user_id, -wager)
    elif player_value == 21 and len(player_hand) == 2 and dealer_value != 21:
        result_message = "Blackjack! You win!"
        update_stats = "UPDATE users SET wins = wins + 1, chip_count = chip_count + %s WHERE discord_id = %s"
        # update_values = (int(1.5 * wager), user_id)
        db.blackjack_result("WIN", user_id, int(1.5 * wager))
    else:
        result_message = "You win!"
        update_stats = "UPDATE users SET wins = wins + 1, chip_count = chip_count + %s WHERE discord_id = %s"
        # update_values = (wager * 2, user_id)
        db.blackjack_result("WIN", user_id, wager * 2)
    
    await ctx.send(result_message)

TOKEN = os.environ.get('BOT_TOKEN')

print(f"Bot token: {TOKEN}")  # Ensure you setup the token right

bot.run(TOKEN)  # Run the bot using the token provided