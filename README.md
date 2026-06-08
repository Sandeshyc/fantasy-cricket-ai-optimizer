# 🏏 Fantasy Cricket AI Optimizer

[![Vue 3](https://img.shields.io/badge/Vue.js-3.0-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/Gen_AI-OpenAI-412991?logo=openai&logoColor=white)](https://openai.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)

A full-stack, AI-powered Fantasy Cricket Team Optimizer. This application helps you build the perfect 11-player squad for any IPL matchup using **Mathematical Optimization (Integer Linear Programming)**, **Data Engineering ETL Pipelines** (processing 16 years of historical ball-by-ball data), and **Generative AI** for strategic scout reports.

---

## ✨ Key Features

### 1. Data Engineering & ETL Pipeline
*   **Raw Data Parsing:** Ingests thousands of raw `.csv` ball-by-ball match files from Cricsheet.
*   **Dynamic Stats Calculation:** Automatically calculates career batting averages, bowling economy, and recent form across 16 seasons.
*   **Automated Role Mapping:** Heuristically classifies 500+ players into pure Batters, Bowlers, or All-Rounders based on career ball-faced to ball-bowled ratios.
*   **PostgreSQL Database:** Streams massive datasets efficiently into a scalable **Supabase** backend using Python.

### 2. Mathematical Optimizer (ILP Solver)
*   **The Knapsack Problem:** Uses the Python `PuLP` library to build the team mathematically.
*   **Strict Constraints Handled:**
    *   Max budget of 100 Credits.
    *   Max 7 players from a single team.
    *   Maximum of 4 Overseas (Foreign) players.
    *   Role constraints (1-4 Wicket Keepers, 3-6 Batters, 1-4 All-Rounders, 3-6 Bowlers).

### 3. Generative AI Scout Report (OpenAI)
*   **Dynamic Matchups:** The backend sends the mathematically generated 11-man squad to OpenAI's `gpt-4o-mini`.
*   **Captaincy Logic:** The LLM analyzes the specific matchup and assigns the best Captain (2x pts) and Vice-Captain (1.5x pts) roles.
*   **Contrarian Wildcards:** The AI scans the benched players and recommends high-risk, high-reward differential picks.
*   **Match Narrative Simulator:** Generates vivid, natural-language simulations of how the team will perform on the pitch.

### 4. Interactive UI/UX
*   **Glassmorphic Draft Arena:** A stunning Vue 3 / TailwindCSS interface for drafting your initial 22-man squad.
*   **Pitch Visualization:** Custom CSS grid rendering players directly onto a virtual cricket pitch.
*   **Live Swapping Engine:** Users can override the AI by clicking a player on the pitch and swapping them out. The UI strictly enforces budget/foreign constraints in real-time.

---

## 📸 App Flow & UI/UX

*(Add your screen recordings or GIFs here for a better portfolio presentation!)*

1.  **Match Selection:** Choose the season and the two teams playing today.
2.  **The Draft Arena:** Draft your 22-player preliminary squad (11 from each team). The UI displays real-time validation for constraints (like the max 4 foreign players limit ✈️).
3.  **AI Optimization Results:** Click **Run AI Optimizer** to solve the knapsack problem! The mathematically perfect 11-man squad is placed onto a virtual pitch.
4.  **Generative AI Scout Report:** Analyzes your team, assigns Captains, and predicts the match narrative. *(Note: Clicking any player on the pitch opens a modal to manually swap benched players or assign C/VC roles, instantly recalculating constraints!)*

---

## 🏗️ Architecture

```mermaid
flowchart TD
    classDef frontend fill:#1e1e1e,stroke:#4FC08D,stroke-width:2px,color:#fff;
    classDef backend fill:#1e1e1e,stroke:#009688,stroke-width:2px,color:#fff;
    classDef database fill:#1e1e1e,stroke:#3ECF8E,stroke-width:2px,color:#fff;
    classDef external fill:#1e1e1e,stroke:#888,stroke-width:2px,color:#fff,stroke-dasharray: 5 5;
    classDef ai fill:#1e1e1e,stroke:#412991,stroke-width:2px,color:#fff;

    subgraph Offline["🛠️ Phase 1: Data Engineering & ETL Pipeline"]
        direction LR
        CSV[/"Raw Cricsheet CSVs"\]:::external -->|Batch Processing| SEED("seed_db.py\n(Pandas Aggregation)"):::backend
        MAP[/"overseas_players.json"\]:::external -->|Role & Origin Mappings| SEED
        SEED -->|Upsert Stats & Profiles| DB[("Supabase\nPostgreSQL")]:::database
    end

    subgraph Online["⚡ Phase 2: Live Inference & App Flow"]
        direction TB
        UI1("DraftArena.vue\n(Vue 3 UI)"):::frontend -->|1. Fetch Initial Roster| DB
        UI1 -->|2. POST /api/optimize\n(22 Drafted Players)| API{"FastAPI Router\n(main.py)"}:::backend
        
        API -->|3. Player Features| ML("ML Service\n(Scikit-Learn Model)"):::backend
        ML -.->|Predicted Fantasy Points| API
        
        API -->|4. Pts + Budget Constraints| ILP("ILP Optimizer\n(PuLP Solver)"):::backend
        ILP -.->|Mathematically Optimal 11| API
        
        API -->|5. Optimal Squad + Benched| AGENT("LLM Agent\n(llm_agent.py)"):::backend
        AGENT <-->|6. Prompt Completion| GPT[["OpenAI API\n(gpt-4o-mini)"]]:::ai
        
        API -->|7. Final JSON Payload| UI2("OptimizationResults.vue\n(Glassmorphic UI)"):::frontend
    end
    
    Offline ~~~ Online
```

---

## 🚀 Local Setup & Installation

### Prerequisites
*   Node.js (v18+)
*   Python (3.10+)
*   An OpenAI API Key
*   A Supabase Account

### 1. Database Setup (Supabase)
1.  Create a new project on [Supabase](https://supabase.com/).
2.  Navigate to the **SQL Editor** in your Supabase dashboard.
3.  Copy the contents of `backend/scripts/create_tables.sql` and run it to initialize the `teams` and `players` tables.

### 2. Backend Setup
Open your terminal and navigate to the `backend` directory:
```bash
cd backend

# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure Environment Variables
# Create a .env file in the backend directory and add your keys:
# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_anon_key
# OPENAI_API_KEY=your_openai_api_key

# 4. Seed the database (Downloads and parses 16 years of data)
python scripts/seed_db.py

# 5. Start the FastAPI server
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
Open a new terminal window and navigate to the `frontend` directory:
```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Start the Vite development server
npm run dev
```
Navigate to the local URL provided by Vite (usually `http://localhost:5173` or `http://localhost:5174`) to use the application!

---

## 👨‍💻 Author
Built to showcase the intersection of **Data Engineering**, **Mathematical Optimization**, and **Generative AI**.
