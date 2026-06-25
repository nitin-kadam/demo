import requests

def get_cricket_captain(team="India", format="T20"):
    """Fetch current captain info using a public cricket API (fallback to hardcoded if API fails)."""
    # Example using CricketData.org (replace with actual API and key if available)
    # This is a placeholder; you can replace with a real API and key
    try:
        # Example endpoint (replace with real one)
        url = f"https://api.cricapi.com/v1/teams?apikey=YOUR_API_KEY&search={team}"
        response = requests.get(url)
        data = response.json()
        # Parse captain info from response (update as per actual API)
        for t in data.get("data", []):
            if t.get("name", "").lower() == team.lower():
                return t.get("captain", {}).get(format, "Not found")
    except Exception:
        pass
    # Fallback: hardcoded info (update as needed)
    if team.lower() == "india" and format.upper() == "T20":
        return "Suryakumar Yadav (as of August 2025)"
    return "Captain info not available"
