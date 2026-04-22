import requests
from dotenv import load_dotenv
import os

load_dotenv()

SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")


def get_recent_orders(since_id=None):
    url = f"{SHOPIFY_STORE_URL}/admin/api/2024-01/orders.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    params = {"status": "any", "limit": 50}
    if since_id:
        params["since_id"] = since_id

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("orders", [])
