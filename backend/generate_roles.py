import glob
import pandas as pd
import json

print("Parsing CSVs to generate definitive roles...")
all_files = [f for f in glob.glob('ipl_raw_data/*.csv') if not f.endswith('_info.csv')]
df_list = []
for file in all_files[:200]:
    temp_df = pd.read_csv(file)
    df_list.append(temp_df)
df = pd.concat(df_list, ignore_index=True)

# Calculate stats
player_stats = {}

for p in df['striker'].unique(): player_stats[p] = {'runs': 0, 'balls_faced': 0, 'balls_bowled': 0, 'wickets': 0}
for p in df['bowler'].unique():
    if p not in player_stats: player_stats[p] = {'runs': 0, 'balls_faced': 0, 'balls_bowled': 0, 'wickets': 0}

# Populate stats
batting = df.groupby('striker').agg(runs=('runs_off_bat', 'sum'), balls=('match_id', 'count')).reset_index()
for _, row in batting.iterrows():
    player_stats[row['striker']]['runs'] = row['runs']
    player_stats[row['striker']]['balls_faced'] = row['balls']

bowling = df.groupby('bowler').agg(wickets=('wicket_type', lambda x: x.notnull().sum()), balls=('match_id', 'count')).reset_index()
for _, row in bowling.iterrows():
    player_stats[row['bowler']]['wickets'] = row['wickets']
    player_stats[row['bowler']]['balls_bowled'] = row['balls']

# Hardcoded WKs
known_wks = ['MS Dhoni', 'KD Karthik', 'Q de Kock', 'KL Rahul', 'RR Pant', 'SV Samson', 'Ishan Kishan', 'WP Saha', 'JM Bairstow', 'JC Buttler', 'N Pooran', 'H Klaasen', 'KS Bharat', 'Dhruv Jurel', 'Jitesh Sharma', 'PD Salt']

roles_map = {}
for p, stats in player_stats.items():
    if p in known_wks:
        roles_map[p] = 'WK'
    elif stats['balls_bowled'] > 60:  # Bowled more than 10 overs in their entire career segment
        if stats['balls_faced'] > 120: # Faced more than 20 overs
            roles_map[p] = 'AR'
        else:
            roles_map[p] = 'BOWL'
    else:
        roles_map[p] = 'BAT'

# Special overrides
roles_map['M Pathirana'] = 'BOWL'
roles_map['SP Narine'] = 'AR'
roles_map['AD Russell'] = 'AR'

with open('player_roles.json', 'w') as f:
    json.dump(roles_map, f, indent=4)

print(f"Generated player_roles.json successfully with {len(roles_map)} players.")
