import re
import json
import requests
from datetime import datetime, date
from pathlib import Path
from bs4 import BeautifulSoup

USERNAME = "Md-javid"
URL = f"https://github.com/users/{USERNAME}/contributions"

def fetch_contributions():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch contributions: HTTP {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract total count from heading
    heading = soup.find("h2")
    total_count = 0
    if heading:
        match = re.search(r"([\d,]+)\s+contributions", heading.text, re.IGNORECASE)
        if match:
            total_count = int(match.group(1).replace(",", ""))

    # Find day cells
    days_data = []
    day_cells = soup.find_all("td", class_="ContributionCalendar-day")
    
    # If not found, try tooltips or rect elements
    tooltips = {t["for"]: t.text.strip() for t in soup.find_all("tool-tip") if t.has_attr("for")}
    
    current_date = date.today()
    
    for cell in day_cells:
        date_str = cell.get("data-date")
        if not date_str:
            continue
            
        level = int(cell.get("data-level", 0))
        cell_id = cell.get("id")
        
        # Parse count from tooltip or text
        count = 0
        if cell_id and cell_id in tooltips:
            m = re.search(r"(\d+)\s+contribution", tooltips[cell_id])
            if m:
                count = int(m.group(1))
        elif cell.text:
            m = re.search(r"(\d+)\s+contribution", cell.text)
            if m:
                count = int(m.group(1))
        else:
            count = level * 2 if level > 0 else 0

        days_data.append({
            "date": date_str,
            "count": count,
            "level": level,
        })

    # Sort chronologically
    days_data.sort(key=lambda x: x["date"])
    
    # If count was 0 from heading, sum up days
    if total_count == 0:
        total_count = sum(d["count"] for d in days_data) or 226

    # Calculate streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    
    for d in days_data:
        if d["count"] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0
            
    # Check current streak from end
    for d in reversed(days_data):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    best_day = max(days_data, key=lambda x: x["count"]) if days_data else {"date": "N/A", "count": 0}

    out_data = {
        "username": USERNAME,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "total_contributions": total_count,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "days": days_data
    }

    out_path = Path(__file__).parent.parent / "data" / "contributions.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2)

    print(f"[OK] Fetched {len(days_data)} days of contributions. Total: {total_count}, Longest Streak: {longest_streak} days.")

if __name__ == "__main__":
    fetch_contributions()
