# test_gnews.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GNEWS_API_KEY')
topic = "technology"
url = f"https://gnews.io/api/v4/search?q={topic}&lang=en&max=1&token={api_key}"

print(f"Testing connection to: {url}")

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    print("\nSUCCESS! Connected to GNews and got a response:")
    print(response.json())
except Exception as e:
    print("\nFAILURE! Could not connect to GNews.")
    print(f"Error details: {e}")