import os
from openai import OpenAI
from typing import List, Dict, Any
import json

def get_openai_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing from environment variables.")
    return OpenAI(api_key=api_key)

def generate_scout_report(team_a: str, team_b: str, optimized_squad: List[Dict[str, Any]], all_drafted: List[Dict[str, Any]]) -> str:
    """
    Generates a comprehensive AI scout report using OpenAI.
    """
    client = get_openai_client()
    
    # Format the squad for the prompt
    squad_list = []
    captain = None
    vice_captain = None
    
    for p in optimized_squad:
        role_info = p.get('role', 'Unknown')
        form_info = f"Proj Pts: {p.get('predicted_points', 0):.1f}"
        
        # In case form_avg_runs or wickets are present
        if 'form_avg_runs' in p:
            form_info += f", Avg Runs: {p['form_avg_runs']}"
        if 'form_avg_wickets' in p:
            form_info += f", Avg Wkts: {p['form_avg_wickets']}"
            
        squad_list.append(f"- {p['name']} ({p['team']}) - Role: {role_info} - {form_info}")
        
        if p.get('is_captain'):
            captain = p['name']
        if p.get('is_vice_captain'):
            vice_captain = p['name']
            
    squad_str = "\n".join(squad_list)
    
    # Format all drafted players to find who was left out
    benched_list = []
    selected_names = set(p['name'] for p in optimized_squad)
    for p in all_drafted:
        if p['name'] not in selected_names:
            role_info = p.get('role', 'Unknown')
            benched_list.append(f"- {p['name']} ({p['team']}) - Role: {role_info}")
    
    benched_str = "\n".join(benched_list) if benched_list else "None"
    
    prompt = f"""
    You are an elite Fantasy Cricket Tactical Analyst and AI Coach analyzing an upcoming T20 match between {team_a} and {team_b}.
    
    CRITICAL INSTRUCTIONS - ANTI-HALLUCINATION GUARDRAILS:
    1. You MUST ONLY use the players explicitly provided in the lists below. DO NOT invent, assume, or hallucinate any other players.
    2. You MUST use the exact team affiliations provided.
    
    The mathematical optimization engine has selected the following 11-man squad based on recent form and stats:
    {squad_str}
    
    The engine has ALREADY assigned {captain} as Captain (2x points) and {vice_captain} as Vice-Captain (1.5x points) due to their highest projected points.
    
    The following players were drafted but left on the bench by the math engine:
    {benched_str}
    
    Please provide a comprehensive "AI Scout Report" in Markdown format containing EXACTLY these 3 sections:
    
    ### 👑 Captain & Vice-Captain Tactical Analysis
    The mathematical engine has assigned {captain} as Captain and {vice_captain} as Vice-Captain based purely on projected statistical points. 
    First, evaluate these algorithmic choices. 
    Next, make your OWN independent, tactical decision for Captain and Vice-Captain from the 11-man squad using deep cricketing logic (e.g., match conditions, all-rounder dual-utility, death bowling). 
    If your tactical choices MATCH the engine's choices, explain why the math aligns perfectly with cricket reality today. 
    If your tactical choices DIFFER from the engine's choices, clearly declare your alternate "AI Coach Picks" and provide a strong cricketing justification for why your tactical intuition overrides the pure statistics.
    
    ### 🃏 The Contrarian Wildcard (Bench Analysis)
    The math engine picks the safest team based on pure statistics. Scan the benched players list above. Select ONE benched player as a high-risk, high-reward "differential pick" that a human manager should consider swapping into the playing 11. Provide a tactical cricketing reason why this player could be a game-changer today (e.g., a wrist-spinner who can exploit a dry pitch, or a hard-hitting finisher). If the bench is empty, strictly state "No bench players available."
    
    ### 🏏 Match Narrative Simulation
    Write a vivid, realistic 3-4 sentence narrative predicting how this specific 11-man team will perform on the pitch today. Describe specific players executing cricketing skills (e.g., hitting down the ground, taking key wickets in the powerplay, or building a crucial partnership). ONLY mention players from the provided 11-man squad.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a strict, factual expert fantasy cricket analyst who never hallucinates players."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return f"**Error generating AI Insights:** Could not reach OpenAI API. Please check your OPENAI_API_KEY. Details: {str(e)}"
