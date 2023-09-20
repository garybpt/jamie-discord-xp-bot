import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pytz import timezone
import os
import asyncio
import json
import random

# Load environment variables from .env file
load_dotenv()

# Get the bot token and role IDs from environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_ID = os.getenv("SERVER_ID")
ERROR_CHANNEL_ID = int(os.getenv("ERROR_CHANNEL_ID"))
LEADERBOARD_CHANNEL_ID = int(os.getenv("LEADERBOARD_CHANNEL_ID"))
ROLE_LVL5_ID = int(os.getenv("ROLE_LVL5_ID"))
ROLE_LVL10_ID = int(os.getenv("ROLE_LVL10_ID"))
ROLE_LVL25_ID = int(os.getenv("ROLE_LVL25_ID"))
ROLE_LVL50_ID = int(os.getenv("ROLE_LVL50_ID"))
ROLE_LVL100_ID = int(os.getenv("ROLE_LVL100_ID"))
ROLE_LVL500_ID = int(os.getenv("ROLE_LVL500_ID"))

LEVEL_UP_MESSAGES=[
    "Hey there, {message.author.mention}. You've achieved level {{user_data[author_id]['level']}}! Keep up the fantastic work on your journey to better wellbeing.",
    "Bravo, {message.author.mention}. You're now at level {{user_data[author_id]['level']}}! Your dedication to self-care and happiness is shining through.",
    "Well done, {message.author.mention}. Level {{user_data[author_id]['level']}} unlocked! Your commitment to personal wellness is truly inspiring.",
    "Look who's climbing the ranks, {message.author.mention}. You've reached level {{user_data[author_id]['level']}}! Keep up the positivity and self-improvement.",
    "Ding, ding, ding, {message.author.mention}. You've made it to level {{user_data[author_id]['level']}}! Your wellbeing journey is definitely on the right track.",
    "Hooray, {message.author.mention}! You have reached level {{user_data[author_id]['level']}}! Keep up with those good vibes.",
    "Way to go, {message.author.mention}. You're now at level {{user_data[author_id]['level']}}! Your focus on wellbeing is paying off in spades.",
    "Achievement unlocked, {message.author.mention}! You're now at level {{user_data[author_id]['level']}}! Continue to prioritise your health and happiness.",
    "You're on fire, {message.author.mention}. Level {{user_data[author_id]['level']}} is yours! Keep nurturing your wellbeing and thriving.",
    "Level up, level up, {message.author.mention}! You've achieved level {{user_data[author_id]['level']}}! The journey toward improved wellbeing continues and you're doing fantastic."
]

NEW_ROLE_MESSAGES=[
    "Outstanding work, {message.author.mention}! Your consistent dedication and contributions to our wellbeing community have earned you the {role.name} role. Continue to enrich our community while nurturing your own growth and wellbeing.",
    "Well-earned, {message.author.mention}! Your reputation for being a caring, committed, and encouraging member of our community has granted you the {role.name} role. Keep uplifting others and discover even more about your own journey to wellbeing.",
    "Congratulations, {message.author.mention}! Your standing as a reliable and respectful member of our wellbeing community has unlocked the {role.name} role. Keep guiding your fellow members and deepen your understanding of wellbeing, benefiting both yourself and the community.",
    "A significant milestone, {message.author.mention}! Your unwavering commitment and respect for others has led you to the {role.name} role. Continue to foster belonging, offer support, and embark on a shared path of growth.",
    "Bravo, {message.author.mention}! Your reputation as a supportive and considerate community member has earned you the {role.name} role. Inspire others and discover fresh perspectives on your own wellbeing journey.",
    "Achievement unlocked, {message.author.mention}! The {role.name} role is yours, a testament to your outstanding reputation, respect, and dedication to our community. Make an enduring positive impact on our members while progressing personally.",
    "Amazing, {message.author.mention}! Your unwavering dedication, respect, and contributions to our wellbeing community have led to the achievement of the {role.name} role. You enhance wellbeing for us all.",
    "Fantastic news, {message.author.mention}! Your ongoing commitment, respect for others, and dedication to our community has resulted in you attaining the {role.name} role. Keep pushing forward, lend a helping hand, and continue your journey of self-improvement and community support.",
    "Impressive work, {message.author.mention}! Your consistent dedication and contributions to our wellbeing community has earned you the {role.name} role. Embrace this opportunity to continue enriching our community with your knowledge and support, while also nurturing your personal growth.",
    "Well-deserved, {message.author.mention}! Your reputation for being a caring, committed, and encouraging member of our community has granted you the {role.name} role. Keep setting a positive example and nurturing the growth of others, as well as your own.",
    "Congratulations, {message.author.mention}! Your standing as a reliable and respectful member of our wellbeing community has unlocked the {role.name} role. Your wisdom and guidance can benefit fellow members on their journey and further enhance your own understanding of wellbeing.",
    "A significant achievement, {message.author.mention}! Your unwavering commitment and respect for others have led you to the {role.name} role. Continue to foster a sense of belonging and offer your support to those in need, all while continuing to grow personally.",
    "Bravo, {message.author.mention}! Your reputation as a supportive and considerate community member has earned you the {role.name} role. Be a beacon of positivity and encouragement to inspire others, while also finding inspiration and growth within yourself.",
    "Well done, {message.author.mention}! Your dedication and efforts to promote respect within our community is off the charts, granting you the {role.name} role. Continue to cultivate a warm and inclusive atmosphere, benefitting both our community and yourself.",
    "Role unlocked, {message.author.mention}! The {role.name} role is yours, a testament to your outstanding reputation, respect, and dedication to our community. Use your influence to make a lasting positive impact on our members and foster personal growth."
]

# Define your time zone (example: GMT)
TIMEZONE = timezone('GMT')

# Define the time for the leaderboard announcement (every Sunday at 20:00 GMT)
LEADERBOARD_TIME = TIMEZONE.localize(datetime.strptime("20:00", "%H:%M")).time()

# Calculate the initial delay to the next Sunday at 20:00 GMT
now = datetime.now(TIMEZONE)
next_sunday = now + timedelta(
    days=(6 - now.weekday()) % 7, hours=20 - now.hour, minutes=0 - now.minute, seconds=0 - now.second
)

# Define a 5-second cooldown for gaining XP
xp_cooldown = commands.cooldown(1, 5.0, commands.BucketType.user)

# Create a bot instance with a command prefix and intents
intents = discord.Intents.default()  # Enable all default intents
intents.typing = False  # Disable typing events to reduce intents usage (optional)

bot = commands.Bot(command_prefix="!", intents=intents)

# Define a filename for the user XP data JSON file
USER_XP_FILENAME = "user-xp.json"

# Function to save user XP data to a JSON file
def save_user_xp():
    with open(USER_XP_FILENAME, "w") as file:
        json.dump(user_data, file)

def load_user_xp():
    if os.path.exists(USER_XP_FILENAME):
        with open(USER_XP_FILENAME, "r") as file:
            try:
                return json.load(file)
            except json.decoder.JSONDecodeError:
                # Handle the case where the file is empty or contains invalid JSON
                return {}
    else:
        return {}

# Load user XP data when the bot starts
user_data = load_user_xp()

# XP needed to level up
XP_THRESHOLD = 100

# Level thresholds and corresponding role IDs
LEVEL_ROLES = {
    5: ROLE_LVL5_ID,
    10: ROLE_LVL10_ID,
    25: ROLE_LVL25_ID,
    50: ROLE_LVL50_ID,
    100: ROLE_LVL100_ID,
    500: ROLE_LVL500_ID
}

# Function to remove user data for inactive members who left the server more than 7 days ago
async def remove_inactive_user_data():
    seven_days_ago = datetime.now() - timedelta(days=7)

    for user_id in list(user_data.keys()):
        member = bot.get_guild(SERVER_ID).get_member(int(user_id))
        if not member or (member.left_at and member.left_at <= seven_days_ago):
            del user_data[user_id]

# Schedule the user data cleanup task (runs daily)
@tasks.loop(hours=24)  # Run every 24 hours
async def cleanup_user_data():
    await bot.wait_until_ready()  # Wait until the bot is ready
    await remove_inactive_user_data()
    save_user_xp()  # Save the updated user data to the JSON file

# Start the cleanup task when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    publish_leaderboard.start()  # Start the leaderboard task
    cleanup_user_data.start()  # Start the user data cleanup task

# Event: User sends a message
@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return  # Skip processing messages from your bot or other bots

    # Check if the message length is less than 10 characters
    if len(message.content) < 10:
        await bot.process_commands(message)  # This line is necessary for cooldowns to work
        return  # Don't award XP for short messages

    # Calculate base XP earned (7 XP per message)
    base_xp = 7

    # Check if the message length is over 180 characters
    if len(message.content) > 180:
        base_xp *= 3  # Triple the XP if the message is longer than 180 characters

    # Check if the message length is over 500 characters
    if len(message.content) > 500:
        base_xp *= 5  # Triple the XP if the message is longer than 500 characters

    # Apply the cooldown to prevent XP gain within 5 seconds
    await bot.process_commands(message)  # This line is necessary for cooldowns to work

    # Increment user's XP
    author_id = str(message.author.id)
    user_data.setdefault(author_id, {"xp": 0, "level": 1, "xp_this_week": 0})
    user_data[author_id]["xp"] += base_xp
    user_data[author_id]["xp_this_week"] += base_xp

    # Check if the user should level up
    if user_data[author_id]["xp"] >= XP_THRESHOLD * user_data[author_id]["level"]:
        user_data[author_id]["level"] += 1

        # Select a random level up message and replace placeholders
        level_up_message = random.choice(LEVEL_UP_MESSAGES).format(
            message=message, author=message.author, user_data=user_data
        )

        await message.channel.send(level_up_message)

        # Check if the user should be assigned a new role
        for level, role_id in LEVEL_ROLES.items():
            if user_data[author_id]["level"] >= level:
                role = discord.utils.get(message.guild.roles, id=role_id)
                if role and role not in message.author.roles:
                    # Select a random new role message and replace placeholders
                    new_role_message = random.choice(NEW_ROLE_MESSAGES).format(
                        message=message, author=message.author, role=role
                    )

                    await message.author.add_roles(role)
                    await message.channel.send(new_role_message)

    # Save user XP data after each message
    save_user_xp()

# Command: Check user's level
@bot.command()
async def level(ctx):
    author_id = str(ctx.author.id)
    if author_id in user_data:
        await ctx.send(
            f"{ctx.author.mention}, you are level {user_data[author_id]['level']} with {user_data[author_id]['xp']} XP."
        )
    else:
        await ctx.send("You haven't earned any XP yet!")

# Command: !ping
@bot.command()
async def example(ctx):
    async with ctx.typing():
        await asyncio.sleep(2)  # Simulate typing for 2 seconds

# Function to send error messages to the error channel
async def log_error(error_message):
    error_channel = bot.get_channel(ERROR_CHANNEL_ID)
    if error_channel:
        await error_channel.send(f"Error: {error_message}")

# Event: Command error
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use !help for a list of available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing argument. Use !help <command> for command usage.")
    else:
        error_message = f"An error occurred: {error}"
        await log_error(error_message)

# Schedule the leaderboard task
@tasks.loop(hours=168)  # Run every 7 days (once a week)
async def publish_leaderboard():
    # Get the current UTC time
    current_time = datetime.now(TIMEZONE).time()

    # Check if it's time to publish the leaderboard
    if current_time == LEADERBOARD_TIME:
        channel = bot.get_channel(LEADERBOARD_CHANNEL_ID)

        if channel:
            await channel.send("This week's results are in...")

            # Sort users by their XP (top 10)
            top_users = sorted(user_data.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]

            # Publish the leaderboard
            leaderboard_message = "```\nTop 10 Most Prolific Community Members:\n\n"
            for idx, (user_id, user_info) in enumerate(top_users, start=1):
                user = bot.get_user(int(user_id))
                if user:
                    leaderboard_message += (
                        f"{idx}. {user.mention} (Lvl {user_info['level']}) - XP: {user_info['xp']}\n"
                    )

            leaderboard_message += "```"

            await channel.send(leaderboard_message)

            # Calculate and publish the "Ones to Watch" leaderboard
            ones_to_watch_users = sorted(user_data.items(), key=lambda x: x[1]["xp_this_week"], reverse=True)
            main_leaderboard_users = [user_id for user_id, _ in top_users]
            ones_to_watch_users = [user_info for user_info in ones_to_watch_users if user_info[0] not in main_leaderboard_users]
            top_ones_to_watch = ones_to_watch_users[:3]

            ones_to_watch_message = "```\nOnes to Watch - Top 3 Users This Week:\n\n"
            for idx, (user_id, user_info) in enumerate(top_ones_to_watch, start=1):
                user = bot.get_user(int(user_id))
                if user:
                    ones_to_watch_message += (
                        f"{idx}. {user.mention} - XP Gained This Week: {user_info['xp_this_week']}\n"
                    )

            ones_to_watch_message += "```"

            await channel.send(ones_to_watch_message)

# Run the bot with the provided token
bot.run(TOKEN)