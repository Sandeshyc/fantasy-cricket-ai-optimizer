import joblib
import pandas as pd
import random
import os

# Load model globally to keep it in memory
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'my11circle_model.pkl')
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Warning: Could not load model from {MODEL_PATH}. {e}")
    model = None

def predict_points(players):
    """
    Given a list of 22 players, load the .pkl model and predict fantasy points.
    Returns a dictionary mapping player.id -> predicted_points.
    """
    predictions = {}
    
    # In a full production system, we would query Supabase here for the historical features
    # 'form_avg_runs' and 'form_avg_wickets' for these specific players.
    # For this POC, we will generate realistic mock features.
    
    feature_list = []
    player_ids = []
    
    for p in players:
        # We now expect 'p' to be a dictionary with the features from Supabase
        runs = p.get('form_avg_runs', 0.0)
        wickets = p.get('form_avg_wickets', 0.0)
            
        feature_list.append({
            'form_avg_runs': runs,
            'form_avg_wickets': wickets
        })
        player_ids.append(p.get('id', str(random.randint(1,1000))))
        
    if model is not None:
        # Create DataFrame matching the model's expected features
        df = pd.DataFrame(feature_list)
        try:
            preds = model.predict(df)
            for pid, pred in zip(player_ids, preds):
                predictions[pid] = float(pred)
            return predictions
        except Exception as e:
            print("Error during prediction, falling back to random:", e)

    # Fallback if model fails or isn't loaded
    for pid in player_ids:
        predictions[pid] = random.uniform(20.0, 80.0)
        
    return predictions
