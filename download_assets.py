import urllib.request
import json
import os
import urllib.parse
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

teams = {
    'CSK': 'Chennai Super Kings',
    'MI': 'Mumbai Indians',
    'RCB': 'Royal Challengers Bengaluru',
    'KKR': 'Kolkata Knight Riders',
    'DC': 'Delhi Capitals',
    'RR': 'Rajasthan Royals',
    'PBKS': 'Punjab Kings',
    'SRH': 'Sunrisers Hyderabad',
    'LSG': 'Lucknow Super Giants',
    'GT': 'Gujarat Titans'
}

players = {
    'Virat Kohli': 'Virat Kohli',
    'MS Dhoni': 'MS Dhoni',
    'Rohit Sharma': 'Rohit Sharma',
    'Jasprit Bumrah': 'Jasprit Bumrah',
    'Hardik Pandya': 'Hardik Pandya',
    'Rishabh Pant': 'Rishabh Pant',
    'KL Rahul': 'KL Rahul',
    'Sanju Samson': 'Sanju Samson',
    'Shubman Gill': 'Shubman Gill',
    'Shreyas Iyer': 'Shreyas Iyer',
    'Ravindra Jadeja': 'Ravindra Jadeja'
}

os.makedirs('frontend/public/logos', exist_ok=True)
os.makedirs('frontend/public/players', exist_ok=True)

def fetch_wiki_image(title, path):
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize=300"
    req = urllib.request.Request(url, headers={'User-Agent': 'FantasyCricketApp/1.0'})
    try:
        data = json.loads(urllib.request.urlopen(req, context=ctx).read())
        pages = data['query']['pages']
        for page_id in pages:
            if 'thumbnail' in pages[page_id]:
                img_url = pages[page_id]['thumbnail']['source']
                with urllib.request.urlopen(img_url, context=ctx) as response, open(path, 'wb') as out_file:
                    out_file.write(response.read())
                print(f"Downloaded {path}")
            else:
                print(f"No image found for {title}")
    except Exception as e:
        print(f"Failed {title}: {e}")

for short, full in teams.items():
    fetch_wiki_image(full, f"frontend/public/logos/{short}.png")

for name in players.keys():
    fetch_wiki_image(name, f"frontend/public/players/{name.replace(' ', '_')}.jpg")

