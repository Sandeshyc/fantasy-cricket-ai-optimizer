-- SQL Script to create tables in Supabase
-- Please run this in the Supabase Dashboard -> SQL Editor

CREATE TABLE IF NOT EXISTS public.teams (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    logo_url TEXT
);

DROP TABLE IF EXISTS public.players;

CREATE TABLE public.players (
    id UUID PRIMARY KEY,
    team_id TEXT REFERENCES public.teams(id),
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    credits FLOAT NOT NULL,
    image_url TEXT,
    form_avg_runs FLOAT DEFAULT 0.0,
    form_avg_wickets FLOAT DEFAULT 0.0,
    season TEXT NOT NULL,
    is_foreign BOOLEAN DEFAULT false
);

-- Disable Row Level Security (RLS) for the Proof-of-Concept so the Anon key can insert/select data
ALTER TABLE public.teams DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.players DISABLE ROW LEVEL SECURITY;
