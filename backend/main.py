from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from services.ml_inference import predict_points
from services.optimizer import optimize_lineup
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = FastAPI(title="Fantasy Cricket AI Optimizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For POC, restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
supabase: Client = create_client(os.environ.get("SUPABASE_URL", ""), os.environ.get("SUPABASE_KEY", ""))

class PlayerData(BaseModel):
    id: str
    team: str
    name: str
    role: str
    credits: float
    form_avg_runs: float = 0.0
    form_avg_wickets: float = 0.0

class OptimizationRequest(BaseModel):
    match_id: str
    team_a: str
    team_b: str
    playing_twenty_two: List[Dict[str, Any]] # We will let the service query supabase if needed, but for now accept the list

@app.get("/")
def read_root():
    return {"status": "Backend is running!"}

@app.get("/api/seasons")
def get_seasons():
    try:
        # Note: in Supabase/PostgREST to get distinct, we just fetch them and distinct in python for simplicity since the table isn't huge.
        response = supabase.table('players').select('season').execute()
        seasons = sorted(list(set([row['season'] for row in response.data])), reverse=True)
        return seasons
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/teams")
def get_teams():
    try:
        response = supabase.table('teams').select('*').execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rosters/{season}/{team_a}/{team_b}")
def get_rosters(season: str, team_a: str, team_b: str):
    try:
        response = supabase.table('players') \
            .select('id, team_id, name, role, credits, image_url, form_avg_runs, form_avg_wickets, is_foreign') \
            .eq('season', season) \
            .in_('team_id', [team_a, team_b]).execute()
        # Transform output slightly to match frontend expectations
        roster = []
        for p in response.data:
            roster.append({
                "id": p['id'],
                "team": p['team_id'],
                "name": p['name'],
                "role": p['role'],
                "credits": p['credits'],
                "image": p['image_url'],
                "form_avg_runs": p['form_avg_runs'],
                "form_avg_wickets": p['form_avg_wickets'],
                "is_foreign": p.get('is_foreign', False)
            })
        return roster
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize")
def optimize_team(request: OptimizationRequest):
    try:
        # 1. ML Inference - Predict points for all 22 players
        predicted_players = predict_points(request.playing_twenty_two)
        
        # 2. Optimization - Solve ILP for best 11
        optimal_team = optimize_lineup(request.playing_twenty_two, predicted_players)
        
        return {
            "match_id": request.match_id,
            "optimal_team": optimal_team
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error during optimization")

class InsightsRequest(BaseModel):
    team_a: str
    team_b: str
    optimal_team: List[Dict[str, Any]]
    all_drafted: List[Dict[str, Any]]

@app.post("/api/insights")
def generate_insights(request: InsightsRequest):
    try:
        from services.llm_agent import generate_scout_report
        report = generate_scout_report(
            request.team_a, 
            request.team_b, 
            request.optimal_team, 
            request.all_drafted
        )
        return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
