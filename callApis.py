import requests
from dotenv import load_dotenv
import os
import aiohttp

load_dotenv()
SECRET_KEY = os.getenv('VAL_API_KEY') 

async def get_last_match(user, tag):
    url = f"https://api.henrikdev.xyz/valorant/v3/matches/eu/{user}/{tag}"

    headers = {
        "Authorization": SECRET_KEY,
        "Accept":"*/*"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as resp:
            matchdata = await resp.json()
    
    data = {
        'metadata': matchdata['data'][0]['metadata'],
        'players': matchdata['data'][0]['players']['all_players'],
        'teams': matchdata['data'][0]['teams']
    }
    
    return data


async def get_last_n_matches(user, tag, n=5):
    """Fetch the last n matches for a user"""
    url = f"https://api.henrikdev.xyz/valorant/v3/matches/eu/{user}/{tag}"

    headers = {
        "Authorization": SECRET_KEY,
        "Accept":"*/*"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as resp:
            matchdata = await resp.json()
    
    matches = []
    for i in range(min(n, len(matchdata['data']))):
        data = {
            'metadata': matchdata['data'][i]['metadata'],
            'players': matchdata['data'][i]['players']['all_players'],
            'teams': matchdata['data'][i]['teams']
        }
        matches.append(data)
    
    return matches

async def get_rank(user, tag):
    url = f"https://api.henrikdev.xyz/valorant/v2/mmr/eu/{user}/{tag}"

    headers = {
        "Authorization": SECRET_KEY,
        "Accept":"*/*"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as resp:
            matchdata = await resp.json()

    return {
        'current': matchdata['data']['current_data']['images']['small'],
        'peak': matchdata['data']['peak_data']['images']['small']
    }