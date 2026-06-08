import pulp

def optimize_lineup(players, predictions):
    """
    Runs Integer Linear Programming to find the optimal 11-player squad.
    """
    # Create the LP object, maximize
    prob = pulp.LpProblem("FantasyCricketOptimization", pulp.LpMaximize)

    # Variables: 1 if player is selected, 0 otherwise
    player_vars = {}
    for p in players:
        player_vars[p['id']] = pulp.LpVariable(f"player_{p['id']}", cat="Binary")

    # Objective Function: Maximize total predicted points
    prob += pulp.lpSum([predictions[p['id']] * player_vars[p['id']] for p in players])

    # Constraints
    # 1. Exact total players = 11
    prob += pulp.lpSum([player_vars[p['id']] for p in players]) == 11

    # 2. Total Budget <= 100
    prob += pulp.lpSum([p['credits'] * player_vars[p['id']] for p in players]) <= 100

    # 3. Max 7 players per team
    teams = list(set([p['team'] for p in players]))
    if len(teams) == 2:
        team_1, team_2 = teams
        prob += pulp.lpSum([player_vars[p['id']] for p in players if p['team'] == team_1]) <= 7
        prob += pulp.lpSum([player_vars[p['id']] for p in players if p['team'] == team_2]) <= 7

    # 3.5 Max 4 Foreign Players
    prob += pulp.lpSum([player_vars[p['id']] for p in players if p.get('is_foreign', False)]) <= 4

    # 4. Role Quotas (WK, BAT, AR, BOWL)
    roles = ['WK', 'BAT', 'AR', 'BOWL']
    for role in roles:
        role_players = [p for p in players if p['role'] == role]
        if role_players:
            prob += pulp.lpSum([player_vars[p['id']] for p in role_players]) >= 1
            prob += pulp.lpSum([player_vars[p['id']] for p in role_players]) <= 8

    # Solve
    prob.solve()

    if pulp.LpStatus[prob.status] != 'Optimal':
        raise ValueError("Mathematical Infeasibility: Cannot form a valid 11-man squad under 100 credits with the drafted 22 players. Try selecting some cheaper players!")

    # Get results
    selected_players = []
    
    selected_ids = [p['id'] for p in players if player_vars[p['id']].varValue == 1.0]
    selected_objs = [p for p in players if p['id'] in selected_ids]
        
    # Sort descending by predicted points to assign Captain and Vice-Captain
    selected_objs.sort(key=lambda p: predictions[p['id']], reverse=True)
    
    for i, p in enumerate(selected_objs):
        role_tag = ""
        pts = predictions[p['id']]
        if i == 0:
            role_tag = "Captain"
            pts *= 2.0
        elif i == 1:
            role_tag = "Vice-Captain"
            pts *= 1.5
        
        selected_players.append({
            "id": p['id'],
            "name": p['name'],
            "team": p['team'],
            "role": p['role'],
            "credits": p['credits'],
            "image": p.get('image', ''),
            "predicted_points": pts,
            "is_captain": i == 0,
            "is_vice_captain": i == 1
        })

    return {"status": "Optimal", "squad": selected_players}
