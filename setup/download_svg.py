import os
import json
import requests
from config import apiJson

SAVE_DIR = "static/media/csapatok"
MAPPING_FILE = "setup/mapping.json"

os.makedirs(SAVE_DIR, exist_ok=True)

# load country mapping (ISO2 -> country name)
with open(MAPPING_FILE, "r", encoding="utf-8") as f:
    country_map = json.load(f)

# reverse map: country name -> ISO2
name_to_code = {v.lower(): k.lower() for k, v in country_map.items()}

teams_url = apiJson["base-url"] + "/teams"
response = requests.get(teams_url, headers=apiJson["headers"])

if response.status_code != 200:
    print("API error:", response.text)
    exit()

teams = response.json().get("teams", [])

FLAG_BASE = "https://flagcdn.io/flags/4x3"

for team in teams:
    team_id = team["id"]
    name = team["name"].strip().lower()

    # football-data gives country name in "area"
    area = team.get("area", {}).get("name", "").strip().lower()

    country_code = name_to_code.get(area)

    if not country_code:
        print(f"No mapping for: {team['name']} ({area})")
        continue

    flag_url = f"{FLAG_BASE}/{country_code}.svg"
    filepath = os.path.join(SAVE_DIR, f"{team_id}.svg")

    try:
        r = requests.get(flag_url, timeout=10)

        if r.status_code != 200:
            print(f"Missing flag for {area} ({country_code})")
            continue

        with open(filepath, "wb") as f:
            f.write(r.content)

        print(f"Saved {team['name']} -> {team_id}.svg")

    except Exception as e:
        print(f"Error downloading {team['name']}:", e)