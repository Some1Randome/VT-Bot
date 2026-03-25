from dotenv import load_dotenv
import os
import aiohttp

load_dotenv()
SECRET_KEY = os.getenv('VAL_API_KEY')
region = "eu"

async def changeregion(new_region):
    global region
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

async def get_stored(user, tag):
    url = f"https://api.henrikdev.xyz/valorant/v1/stored-matches/{region}/{user}/{tag}"
    headers = {
        "Authorization": SECRET_KEY,
        "Accept":"*/*"
    }
    params = {
        'mode': "competitive",
        'size': 50
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers, params=params) as resp:
            matchdata = await resp.json()

    def extract_data(matchdata):
        total_matches = len(matchdata['data'])
        extracted_data = {
            'matches': total_matches,
            'kills': 0,
            'deaths': 0,
            'score': 0,
            'wins': 0,
            'shots': {
                'head': 0,
                'body': 0,
                'leg': 0
            }
        }
        def didWin(matchdata):
            if matchdata['teams']['red'] == matchdata['teams']['blue']:
                return None
            if matchdata['teams']['red'] > matchdata['teams']['blue']:
                return "red"
            else:
                return "blue"
        for i in range(total_matches):
            data = matchdata['data'][i]
            stats = data.get('stats', {})
            if not stats:
                continue
            winner = didWin(data)
            extracted_data['kills'] += stats.get('kills', 0)
            extracted_data['deaths'] += stats.get('deaths', 0)
            extracted_data['score'] += stats.get('score', 0)
            if winner is stats.get('team', 0):
                extracted_data['wins'] += 1
            shots = stats.get('shots', {})
            extracted_data['shots']['head'] += shots.get('head', 0)
            extracted_data['shots']['body'] += shots.get('body', 0)
            extracted_data['shots']['leg'] += shots.get('leg', 0)
        
        extracted_data['totalshots'] = (extracted_data['shots']['head'] + 
                                       extracted_data['shots']['body'] + 
                                       extracted_data['shots']['leg'])
        return extracted_data
    
    return extract_data(matchdata=matchdata)