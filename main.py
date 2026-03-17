import discord
from discord.ext import commands
import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!vt ", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Commands synced instantly")

@bot.tree.command(name="ping", description="Hallo dome")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!", ephemeral=True)



@bot.command()
async def pping(ctx):
    await ctx.send("Pong!")

bot.run(BOT_TOKEN)