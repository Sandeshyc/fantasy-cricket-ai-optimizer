import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI

# Load env
load_dotenv()

# Setup Supabase
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Setup OpenAI
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def identify_overseas_players():
    print("1. Fetching current domestic players from Supabase...")
    # Fetch all domestic players
    response = supabase.table('players').select('name').eq('is_foreign', False).execute()
    
    # Get unique names
    unique_names = list(set([row['name'] for row in response.data]))
    print(f"Found {len(unique_names)} unique players classified as domestic.")

    print("2. Querying OpenAI to identify misclassified foreign players...")
    # Chunk the list into 150 players per batch to avoid LLM token limits/confusion
    chunk_size = 150
    chunks = [unique_names[i:i + chunk_size] for i in range(0, len(unique_names), chunk_size)]
    
    newly_identified_foreigners = set()

    for idx, chunk in enumerate(chunks):
        print(f"   Processing chunk {idx + 1}/{len(chunks)}...")
        
        prompt = f"""
You are a cricket historian. I will give you a list of cricket players who have played in the Indian Premier League (IPL) from 2008-2026.
Your job is to identify ONLY the players who are OVERSEAS (not from India).
Return a JSON array of strings containing the EXACT names of the overseas players from the list.
Do not return any markdown formatting, just the raw JSON array.

List of players:
{json.dumps(chunk)}
"""
        try:
            completion = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            
            raw_response = completion.choices[0].message.content.strip()
            # Clean markdown if the LLM ignores instructions
            if raw_response.startswith('```json'):
                raw_response = raw_response[7:-3].strip()
            if raw_response.startswith('```'):
                raw_response = raw_response[3:-3].strip()
                
            foreigners = json.loads(raw_response)
            for f in foreigners:
                newly_identified_foreigners.add(f)
        except Exception as e:
            print(f"Error processing chunk {idx+1}: {e}")

    print(f"\nIdentified {len(newly_identified_foreigners)} new overseas players!")

    if len(newly_identified_foreigners) > 0:
        print("3. Updating data/overseas_players.json...")
        json_path = "data/overseas_players.json"
        
        # Load existing
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                overseas_map = json.load(f)
        else:
            overseas_map = {}
            
        # Append new
        for player in newly_identified_foreigners:
            overseas_map[player] = True
            
        # Save back
        with open(json_path, 'w') as f:
            json.dump(overseas_map, f, indent=4)
            
        print("4. Updating Supabase database...")
        # Supabase `.in_` clause has URL length limits, so we update one by one or in small batches
        success_count = 0
        for player in newly_identified_foreigners:
            try:
                supabase.table('players').update({'is_foreign': True}).eq('name', player).execute()
                success_count += 1
            except Exception as e:
                print(f"Failed to update {player} in DB: {e}")
                
        print(f"Successfully updated {success_count} players in the database.")
    else:
        print("No new overseas players were found. Data is perfectly clean!")

if __name__ == "__main__":
    identify_overseas_players()
