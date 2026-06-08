import urllib.request
import zipfile
import glob
import pandas as pd
import os
import random
import uuid
import json
import ssl
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("1. Downloading Cricsheet data...")
if not os.path.exists("ipl_data.zip"):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen("https://cricsheet.org/downloads/ipl_csv2.zip", context=ctx) as response, open("ipl_data.zip", 'wb') as out_file:
        out_file.write(response.read())

print("2. Unzipping data...")
os.makedirs("ipl_raw_data", exist_ok=True)
with zipfile.ZipFile("ipl_data.zip", 'r') as zip_ref:
    zip_ref.extractall("ipl_raw_data")

print("3. Parsing ball-by-ball files...")
all_files = [f for f in glob.glob('ipl_raw_data/*.csv') if not f.endswith('_info.csv')]

df_list = []
# Process all historical matches to extract every season (e.g., 2008 to 2026)
for file in all_files:
    temp_df = pd.read_csv(file)
    df_list.append(temp_df)

df = pd.concat(df_list, ignore_index=True)

print("4. Calculating Player Stats & Form per Season...")

df['season'] = df['season'].astype(str)

# Batting stats per season
batting = df.groupby(['striker', 'season']).agg(
    total_runs=('runs_off_bat', 'sum'),
    matches_played=('match_id', 'nunique'),
    team=('batting_team', 'last')
).reset_index()
batting['form_avg_runs'] = batting['total_runs'] / batting['matches_played']

# Bowling stats per season
bowling = df.groupby(['bowler', 'season']).agg(
    total_wickets=('wicket_type', lambda x: x.notnull().sum()),
    matches_played=('match_id', 'nunique'),
    team=('bowling_team', 'last')
).reset_index()
bowling['form_avg_wickets'] = bowling['total_wickets'] / bowling['matches_played']

teams_map = {
    'Chennai Super Kings': 'CSK',
    'Mumbai Indians': 'MI',
    'Royal Challengers Bangalore': 'RCB',
    'Royal Challengers Bengaluru': 'RCB',
    'Kolkata Knight Riders': 'KKR',
    'Delhi Capitals': 'DC',
    'Rajasthan Royals': 'RR',
    'Punjab Kings': 'PBKS',
    'Kings XI Punjab': 'PBKS',
    'Sunrisers Hyderabad': 'SRH',
    'Lucknow Super Giants': 'LSG',
    'Gujarat Titans': 'GT'
}

# Merge all players per season
# We want unique (player, season)
season_players = set()
for _, row in batting.iterrows():
    season_players.add((row['striker'], row['season']))
for _, row in bowling.iterrows():
    season_players.add((row['bowler'], row['season']))

# Load roles from generated JSON map
with open('player_roles.json', 'r') as f:
    player_roles_map = json.load(f)

# Load overseas map
with open('data/overseas_players.json', 'r') as f:
    overseas_players_map = json.load(f)

players_data = []

for p_name, season in season_players:
    bat_row = batting[(batting['striker'] == p_name) & (batting['season'] == season)]
    bowl_row = bowling[(bowling['bowler'] == p_name) & (bowling['season'] == season)]
    
    avg_runs = bat_row['form_avg_runs'].values[0] if not bat_row.empty else 0.0
    avg_wkts = bowl_row['form_avg_wickets'].values[0] if not bowl_row.empty else 0.0
    
    # Team (prefer batting, fallback to bowling)
    team_full = 'Chennai Super Kings'
    if not bat_row.empty:
        team_full = bat_row['team'].values[0]
    elif not bowl_row.empty:
        team_full = bowl_row['team'].values[0]
        
    team_id = teams_map.get(team_full, 'CSK')
    
    role = player_roles_map.get(p_name, 'BAT')
        
    is_foreign = p_name in overseas_players_map
        
    players_data.append({
        'id': str(uuid.uuid4()),
        'team_id': team_id,
        'name': p_name,
        'role': role,
        'credits': round(random.uniform(7.5, 11.0) * 2) / 2, # Mock credits
        'image_url': f"https://ui-avatars.com/api/?name={p_name.replace(' ', '+')}&background=random",
        'form_avg_runs': round(avg_runs, 2),
        'form_avg_wickets': round(avg_wkts, 2),
        'season': season,
        'is_foreign': is_foreign
    })

teams_data = [
    {'id': 'CSK', 'name': 'Chennai Super Kings', 'logo_url': '/logos/csk.png'},
    {'id': 'MI', 'name': 'Mumbai Indians', 'logo_url': '/logos/mi.png'},
    {'id': 'RCB', 'name': 'Royal Challengers Bengaluru', 'logo_url': '/logos/rcb.png'},
    {'id': 'KKR', 'name': 'Kolkata Knight Riders', 'logo_url': '/logos/kkr.png'},
    {'id': 'DC', 'name': 'Delhi Capitals', 'logo_url': '/logos/dc.png'},
    {'id': 'RR', 'name': 'Rajasthan Royals', 'logo_url': '/logos/rr.png'},
    {'id': 'PBKS', 'name': 'Punjab Kings', 'logo_url': '/logos/pbks.png'},
    {'id': 'SRH', 'name': 'Sunrisers Hyderabad', 'logo_url': '/logos/srh.png'},
    {'id': 'LSG', 'name': 'Lucknow Super Giants', 'logo_url': '/logos/lsg.svg'},
    {'id': 'GT', 'name': 'Gujarat Titans', 'logo_url': '/logos/gt.svg'}
]

print("5. Uploading to Supabase...")
try:
    # Insert teams
    supabase.table('teams').upsert(teams_data).execute()
    print("Inserted teams!")
    
    # Clear existing players to avoid duplicates
    supabase.table('players').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    
    # Insert players in batches
    batch_size = 50
    for i in range(0, len(players_data), batch_size):
        batch = players_data[i:i+batch_size]
        supabase.table('players').insert(batch).execute()
    print(f"Inserted {len(players_data)} seasonal player records!")
except Exception as e:
    print("Database upload failed. Did you create the tables in Supabase first?", e)
