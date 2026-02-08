import requests
import os
from datetime import datetime, timedelta
import pytz

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
TEAM_ID = 64  # Liverpool
BASE_URL = "https://api.football-data.org/v4"

headers = {"X-Auth-Token": API_KEY}

competitions = ["PL", "CL", "FAC", "ELC"]
matches = []

for comp in competitions:
    url = f"{BASE_URL}/teams/{TEAM_ID}/matches?competitions={comp}&season=2026"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        matches.extend(r.json().get("matches", []))

brt = pytz.timezone("America/Sao_Paulo")

ics = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Liverpool Calendar//EN",
    "CALSCALE:GREGORIAN"
]

for m in matches:
    utc = pytz.utc.localize(datetime.fromisoformat(m["utcDate"].replace("Z", "")))
    start = utc.astimezone(brt)
    end = start + timedelta(hours=2)

    title = f"Liverpool x {m['awayTeam']['name']}" if m["homeTeam"]["id"] == TEAM_ID else f"{m['homeTeam']['name']} x Liverpool"

    ics.extend([
        "BEGIN:VEVENT",
        f"UID:{m['id']}@liverpool-calendar",
        f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
        f"DTSTART:{start.strftime('%Y%m%dT%H%M%S')}",
        f"DTEND:{end.strftime('%Y%m%dT%H%M%S')}",
        f"SUMMARY:{title}",
        f"DESCRIPTION:{m['competition']['name']}",
        "BEGIN:VALARM",
        "TRIGGER:-P1D",
        "ACTION:DISPLAY",
        "DESCRIPTION:Lembrete 1 dia antes",
        "END:VALARM",
        "BEGIN:VALARM",
        "TRIGGER:-PT30M",
        "ACTION:DISPLAY",
        "DESCRIPTION:Lembrete 30 minutos antes",
        "END:VALARM",
        "END:VEVENT"
    ])

ics.append("END:VCALENDAR")

with open("liverpool_2026_brt.ics", "w", encoding="utf-8") as f:
    f.write("\n".join(ics))
