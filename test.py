import requests
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env file
API_KEY = os.getenv("IMMICH_API_KEY")
IMMICH_URL = "http://localhost:2283"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}

resp = requests.post(
    f"{IMMICH_URL}/api/search/metadata",
    headers=HEADERS,
    json={"page": 1, "size": 5, "type": "IMAGE", "filters": {}}
)
data = resp.json()
from pprint import pprint
pprint(data["assets"]["items"][0])

