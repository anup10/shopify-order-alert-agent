import requests
from dotenv import load_dotenv
import os

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_order_alert(order):
    order_id = order.get("id")
    order_number = order.get("order_number")
    total_price = order.get("total_price")
    currency = order.get("currency")
    customer = order.get("customer", {})
    customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or "Guest"

    message = {
        "text": f":shopping_bags: New Shopify Order #{order_number}",
        "attachments": [
            {
                "color": "#36a64f",
                "fields": [
                    {"title": "Order ID", "value": str(order_id), "short": True},
                    {"title": "Customer", "value": customer_name, "short": True},
                    {"title": "Total", "value": f"{total_price} {currency}", "short": True},
                ],
            }
        ],
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=message)
    response.raise_for_status()
