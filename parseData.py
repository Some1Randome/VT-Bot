def split_teams(players):
    red = []
    blue = []

    for player in players:
        if player["team"] == "Red":
            red.append(player)
        else:
            blue.append(player)

    return red, blue


def get_match_summary(match_data, username=None, tag=None):
    """Extract basic info from match data: map, agent, and result"""
    metadata = match_data['metadata']
    players = match_data['players']
    teams = match_data['teams']
    
    # Find the player's agent and team result
    user_agent = None
    user_team = None
    user_won = False
    
    for player in players:
        # Find the queried player by username and tag
        if username and tag:
            if player['name'].lower() == username.lower() and player['tag'] == tag:
                user_agent = player['character']
                user_team = player['team']
                break
        else:
            # Fallback to first player if no credentials provided
            user_agent = player['character']
            user_team = player['team']
            break
    
    if user_team == "red":
        user_won = teams['red']['has_won']
    else:
        user_won = teams['blue']['has_won']
    
    result = "✅ Victory" if user_won else "❌ Defeat"
    map_name = metadata['map']
    
    return {
        'map': map_name,
        'agent': user_agent,
        'result': result,
        'won': user_won
    }


def format_matches_selection(matches, username=None, tag=None):
    """Format 5 matches for selection with emoji reactions"""
    selection_msg = "**Select a match:** (React with the corresponding number)\n\n"
    
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    
    for i, match in enumerate(matches):
        summary = get_match_summary(match, username, tag)
        map_name = summary['map']
        agent = summary['agent']
        result = summary['result']
        
        selection_msg += f"{emojis[i]} **Map:** {map_name} | **Agent:** {agent} | {result}\n"
    
    return selection_msg, emojis


def format_match_data(match_data):
    metadata = match_data['metadata']
    players = match_data['players']
    teams = match_data['teams']
    
    red, blue = split_teams(players)
    
    red_score = teams['red']['has_won']
    winner = "Red Team" if red_score else "Blue Team"
    
    map_name = metadata['map']
    game_mode = metadata['mode']
    
    def format_team(team_players, team_name):
        formatted = f"\n**{team_name}:**\n"
        for player in team_players:
            name = player['name']
            tag = player['tag']
            kills = player['stats']['kills']
            deaths = player['stats']['deaths']
            assists = player['stats']['assists']
            rank = player['currenttier_patched']
            formatted += f"`{name}#{tag}` - K: {kills} | D: {deaths} | A: {assists} - `{rank}`\n"
        return formatted
    
    result = f"**Map:** {map_name}\n**Mode:** {game_mode}\n**Winner:** {winner}\n"
    result += format_team(red, "🔴 Red Team")
    result += format_team(blue, "🔵 Blue Team")
    
    return result