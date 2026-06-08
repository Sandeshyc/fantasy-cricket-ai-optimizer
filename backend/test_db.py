import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

res = supabase.table('players').select('name').execute()
names = set(r['name'] for r in res.data)
print(f"Total Unique Players in DB: {len(names)}")
