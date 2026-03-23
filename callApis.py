from dotenv import load_dotenv
import os
import aiohttp

load_dotenv()
SECRET_KEY = os.getenv('VAL_API_KEY')
region = "eu"

async def changeregion(new_region):
    old_region = region
    try:
        region = new_region
        return f"succsesfuly changed region to {new_region} from {old_region}"
    except:
        region = old_region
        return f"an error accured while swaping the region (region: {old_region})"

async def get_last_match(user, tag):
    url = f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{user}/{tag}"

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
    url = f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{user}/{tag}"

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
    url = f"https://api.henrikdev.xyz/valorant/v2/mmr/{region}/{user}/{tag}"

    headers = {
        "Authorization": SECRET_KEY,
        "Accept":"*/*"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as resp:
            matchdata = await resp.json()

    return {
        'current': matchdata['data']['current_data']['images']['small'],
        'peak': matchdata['data']['highest_rank']['patched_tier'],
        'rr': matchdata['data']['current_data']['ranking_in_tier'],
        'elo': matchdata['data']['current_data']['elo']
    }