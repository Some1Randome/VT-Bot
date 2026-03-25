from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from callApis import get_last_match, get_last_n_matches, get_rank, changeregion, get_stored
from parseData import format_match_data, format_matches_selection
from userDataSaveGet import get_user, save_new_user, remove_user

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!vt ", intents=intents)
match_cache = {}


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Commands synced instantly")


@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    
    if payload.message_id not in match_cache:
        return
    
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = await bot.fetch_user(payload.user_id)
    
    matches, username, tag = match_cache[payload.message_id]
    
    emoji_map = {"1️⃣": 0, "2️⃣": 1, "3️⃣": 2, "4️⃣": 3, "5️⃣": 4}
    
    if str(payload.emoji) in emoji_map:
        match_index = emoji_map[str(payload.emoji)]
        
        if match_index < len(matches):
            selected_match = matches[match_index]
            formatted_message = format_match_data(selected_match)            
            await channel.send(f"**Match details for {username}#{tag}:**\n{formatted_message}")
            del match_cache[payload.message_id]


@bot.tree.command(name="ping", description="test bot avalibility by returning pong!")
async def pong(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!", ephemeral=True)


@bot.tree.command(name="getlast5matchs", description="Get the data from the last 5 matches you played by username and tag")
async def getmatch(interaction: discord.Interaction, username: str = None, tag: str = None):
    try:
        await interaction.response.defer()
        
        if username is None or tag is None:
            user_data = get_user(interaction.user.id)
            if user_data is None:
                await interaction.followup.send("No username/tag provided and no saved user data found. Use `/saveriotinfo` to save your account.", ephemeral=True)
                return
            username = user_data['username']
            tag = user_data['tag']
        
        matches = await get_last_n_matches(username, tag, 5)        
        selection_msg, emojis = format_matches_selection(matches, username, tag)        
        message = await interaction.followup.send(selection_msg)
        
        for emoji in emojis[:len(matches)]:
            await message.add_reaction(emoji)

        match_cache[message.id] = (matches, username, tag)
        
    except Exception as e:
        await interaction.followup.send(f"Error fetching match data: {str(e)}")

@bot.tree.command(name="getmatch", description="Get the last match you played by account name and tag")
async def getlastmatch(interaction: discord.Interaction, username: str = None, tag: str = None):
    try:
        await interaction.response.defer()
        if username is None or tag is None:
            user_data = get_user(interaction.user.id)
            if user_data is None:
                await interaction.followup.send("No username/tag provided and no saved user data found. Use `/saveriotinfo` to save your account.", ephemeral=True)
                return
            username = user_data['username']
            tag = user_data['tag']
        
        match = await get_last_match(user=username, tag=tag)
        message = format_match_data(match)
        await interaction.followup.send(message)
    except Exception as e:
        await interaction.followup.send(f"Error fetching match data: {str(e)}")

@bot.tree.command(name="saveriotinfo", description="Link your riot User and tag to your User ID")
async def reguser(interaction: discord.Interaction, username: str, tag: str):
    try:
        save_new_user(interaction.user.id, username=username, tag=tag)
        await interaction.response.send_message(f"Saved Username: {username}, tag: {tag}, to user: {interaction.user.id}", ephemeral=True)
    except:
        await interaction.response.send_message("Failed to save user. Try again later", ephemeral=True)

@bot.tree.command(name="removesavedriotinfo", description="Remove your saved riot ID")
async def removeUser(interaction: discord.Interaction):
    if remove_user(interaction.user.id):
        await interaction.response.send_message(f"Successfully removed your saved riot info", ephemeral=True)
    else:
        await interaction.response.send_message("Failed to remove user data", ephemeral=True)

@bot.tree.command(name="stats", description='Get an estimate of your stats')
async def getStats(interaction: discord.Interaction, username: str = None, tag: str = None, hidden: bool = True):
    try:
        await interaction.response.defer(ephemeral=hidden)
        if username == None or tag == None:
            user_data = get_user(interaction.user.id)
            if user_data == None:
                await interaction.followup.send("No username/tag provided and no saved user data found. Use `/saveriotinfo` to save your account.", ephemeral=hidden)
                return
            username = user_data['username']
            tag = user_data['tag']

        data = await get_stored(user=username, tag=tag)
        
        if data['matches'] == 0 or data['totalshots'] == 0:
            await interaction.followup.send("No match data available for this user.")
            return
        
        embed = discord.Embed(
            title=f"Stats of {username}",
            color=discord.Color.green()
        )

        embed.add_field(name="Average / game:",
                         value=f"Kills: {data['kills'] / data['matches']:.2f}\n"
                         f"Deaths: {data['deaths'] / data['matches']:.2f}\n"
                         f"Score: {data['score'] / data['matches']:.0f}",
                           inline=False)
        embed.add_field(name="Winrate %", value=f"{(data['wins'] / data['matches']) * 100:.1f}%", inline=False)
        embed.add_field(name="Hit %", value=f"Headshot %: {(data['shots']['head'] / data['totalshots']) * 100:.1f}%\n"
                        f"Bodyshot %: {(data['shots']['body'] / data['totalshots']) * 100:.1f}%\n"
                        f"Legshot %: {(data['shots']['leg'] / data['totalshots']) * 100:.1f}%\n",
                        inline=False)
        embed.set_footer(text=f"Data used to get these stats are from the users last {data['matches']} competitive games")
        await interaction.followup.send(embed=embed, ephemeral=hidden)
    except Exception as e:
        await interaction.followup.send(f"An error occured: {e}")
        

@bot.tree.command(name="getrank", description="Get the rank of any given player")
async def getrank(interaction: discord.Interaction, username: str = None, tag: str = None, hidden: bool = True):
    try:
        await interaction.response.defer(ephemeral=hidden)
        
        if username == None or tag == None:
            user_data = get_user(interaction.user.id)
            if user_data == None:
                await interaction.followup.send("No username/tag provided and no saved user data found. Use `/saveriotinfo` to save your account.", ephemeral=True)
                return
            username = user_data['username']
            tag = user_data['tag']
        
        rank_data = await get_rank(user=username, tag=tag)
        
        current_embed = discord.Embed(
            title="Current Rank",
            color=discord.Color.blue()
        )
        current_embed.set_thumbnail(url=rank_data['current'])
        current_embed.add_field(name=username, value=f"#{tag}", inline=False)
        current_embed.add_field(name="RR:", value=rank_data["rr"], inline=False)
        current_embed.add_field(name="MMR:", value=rank_data["elo"], inline=False)
        
        peak_embed = discord.Embed(
            title="Peak Rank",
            color=discord.Color.gold()
        )
        peak_embed.add_field(name=username, value=rank_data['peak'], inline=False)
        
        await interaction.followup.send(embeds=[current_embed, peak_embed])
    except Exception as e:
        await interaction.followup.send(f"Error fetching rank data: {str(e)}", ephemeral=True)

@bot.tree.command(name="mmrrange", description="Get the MMR range of evert rank")
async def printmmr(interaction: discord.Interaction):
    await interaction.response.send_message("mmr list:\n0–800    Iron\n800–1200    Bronze\n1200–1500    Silver\n1500–1700    Gold–Low Diamond\n1700–1900    Diamond–Ascendant\n1900–2200    Ascendant–Immortal\n2200+    Immortal–Radiant", ephemeral=True)  

@bot.tree.command(name="changeregion", description="Change the region your account is registored in")
async def newreg(interaction: discord.Interaction, region: str = 'eu'):
    response = await changeregion(region)
    await interaction.response.send_message(response, ephemeral=True)

@bot.tree.command(name="help", description="Get help on how to use the bot")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Valorant Stats Bot - Help",
        description="Complete guide to using all commands",
        color=discord.Color.red()
    )
    
    embed.add_field(
        name="/ping",
        value="Test if the bot is online",
        inline=False
    )
    
    embed.add_field(
        name="/saveriotinfo",
        value="Save your Riot username and tag\n"
              "**Usage:** `/saveriotinfo username:YourName tag:YourTag`\n"
              "After saving, you won't need to enter credentials in other commands!",
        inline=False
    )
    
    embed.add_field(
        name="/getmatch",
        value="Get your last match details\n"
              "**Usage:** `/getmatch` (if saved) or `/getmatch username:Name tag:Tag`\n"
              "Shows: Map, Mode, Winner, and all player stats",
        inline=False
    )
    
    embed.add_field(
        name="/getlast5matchs",
        value="Get your last 5 matches with selection\n"
              "**Usage:** `/getlast5matchs` (if saved) or `/getlast5matchs username:Name tag:Tag`\n"
              "Shows: Map, Agent, Win/Loss for each match\n"
              "React with 1️⃣-5️⃣ to see full details for a match",
        inline=False
    )
    embed.add_field(
        name="/removesavedriotinfo",
        value="Removes the riot data you saved to your user ID\n" 
        "**Usage:** `/removesavedriotinfo` and that's it\n" 
        "After removing your Info you can add new info\n" 
        "You cant remove others info obviously",
        inline=False
    )

    embed.add_field(
        name="/getrank",
        value="Get the rank of any player based on name and tag\n"
                "**Usage**: `/getrank hidden:False` (if saved) or `/getrank username:Name tag:Tag hidden:False`\n"
                "hidden referse to the messag being ephermal meaning that you are the only one who can read it **false = anyone can see it**"
                "Shows: Current Rank, Peak rank",
        inline=False
    )
    
    embed.add_field(
        name="/mmrrange",
        value="Get the mmr value of every rank\n"
        "**Usage:** `/mmrrange` thats it\n"
        "Shows: The rank   mmr-rating, for every rank in the game"
    )

    embed.add_field(
        name="/stats",
        value="Get a sum of you last 50 competetiv games\n"
        "**Usage:** `/stats hidden:False` (if saved) or `/stats username:Name tag:Tag hidden:False`\n"
        "Shows: Gives back a average of kills, deaths and score(score is not the same as the Valo tracker website but what riot saves 0-10000) and estimete of headshot bodyshot and legshot %",
        inline=False
    )

    embed.add_field(
        name=" Important Notice",
        value="• All match data you pull is **publicly visible** in the channel\n"
              "• Anyone can look up your matches if they have your username\n"
              "• If you use `/saveriotinfo` after already saving your data the old one will be overidden without confirmation",
        inline=False
    )
    
    embed.set_footer(text="Need more help? Try the commands yourself! Or message the developer (Some1Randome)")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.run(token=BOT_TOKEN)