# Python 3.10+, GitHub Actions — r/robloxhackers → Discord
import os
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# --- YOUR NEW WEBHOOK ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1563146584307400825/YvqFQqRWEBcRntUMZBLt3ZUd9SzVn87HNQftJMDNmuGYy3d3LPrWiHLqfzRBy3DaYSrd"

# --- SUBREDDIT FEED ---
FEED_URL = "https://www.reddit.com/r/robloxhackers/new/.rss"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

SEEN_FILE = "reddit_seen.txt"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        f.write("\n".join(seen))

def send_discord(title, author, url):
    payload = {
        "embeds": [{
            "title": title[:256],
            "url": url,
            "description": f"**Author:** u/{author}\n**Subreddit:** r/robloxhackers",
            "color": 0xFF4500, # Reddit Orange
            "footer": {"text": "Reddit Intel"}
        }]
    }
    try:
        r = requests.post(WEBHOOK_URL, json=payload, headers=HEADERS, timeout=15)
        print(f"[hook] {r.status_code} :: {title[:60]}")
        time.sleep(1)
    except Exception as e:
        print(f"[hook] error: {e}")

def check_reddit():
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"[{current_time}] [reddit] checking r/robloxhackers...")
    
    seen = load_seen()
    is_first_run = len(seen) == 0

    try:
        r = requests.get(FEED_URL, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            print(f"[reddit] error: status {r.status_code}")
            return

        # Parse the Atom XML feed
        root = ET.fromstring(r.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # Reddit RSS returns entries in order (newest first)
        entries = root.findall('atom:entry', ns)
        
        # Reverse so we process oldest to newest
        for entry in reversed(entries):
            link = entry.find('atom:link', ns).attrib['href']
            
            if link in seen:
                continue
            
            seen.add(link)
            
            if is_first_run:
                continue
            
            title = entry.find('atom:title', ns).text
            author = entry.find('atom:author/atom:name', ns).text
            
            send_discord(title, author, link)
            
    except Exception as e:
        print(f"[reddit] error: {e}")

    if is_first_run:
        print(f"[reddit] baseline cached: {len(seen)} posts. Waiting for new ones.")
    
    save_seen(seen)

if __name__ == "__main__":
    print("Starting Reddit Intel loop...")
    start_time = time.time()
    
    while time.time() - start_time < 21000:
        check_reddit()
        print("Sleeping for 60 seconds...")
        time.sleep(60)
