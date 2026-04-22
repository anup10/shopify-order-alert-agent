import requests
from dotenv import load_dotenv
from shopify_client import get_customer
import os

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_order_alert(order):
    order_id = order.get("id")
    order_number = order.get("order_number")
    total_price = order.get("total_price")
    currency = order.get("currency")
    customer = order.get("customer") or {}
    customer_name = (
        f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
        or (order.get("billing_address") or {}).get("name", "").strip()
        or (order.get("shipping_address") or {}).get("name", "").strip()
    )
    if not customer_name and customer.get("id"):
        full_customer = get_customer(customer["id"])
        customer_name = (
            f"{full_customer.get('first_name', '')} {full_customer.get('last_name', '')}".strip()
            or full_customer.get("email", "")
            or "Guest"
        )

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
