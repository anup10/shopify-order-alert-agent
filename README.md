# Shopify Order Alert Agent

A lightweight Python agent that monitors your Shopify store in real time and sends instant Slack notifications for new orders above a configurable dollar threshold. Built for e-commerce teams who need immediate visibility into high-value orders without logging into Shopify.

---

## What It Does

- Polls the Shopify Admin API on a configurable interval (default: every 1 minute)
- Filters orders by a minimum order value (default: $250)
- Sends a formatted alert to a Slack channel for every qualifying new order
- Tracks processed orders persistently so no duplicate alerts are sent across sessions or restarts
- Enforces a single-instance lock to prevent accidental concurrent runs

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.x |
| Order Data | Shopify Admin REST API |
| Notifications | Slack Incoming Webhooks |
| Scheduling | APScheduler (BlockingScheduler) |
| Configuration | python-dotenv |

---

## Project Structure

```
shopify-order-alert-agent/
├── main.py              # Scheduler, lock management, and order filtering
├── shopify_client.py    # Shopify Admin API integration
├── slack_notifier.py    # Slack webhook message formatting and delivery
├── .env                 # Environment variables (not committed)
├── .state.json          # Runtime state: seen order IDs (not committed)
├── .agent.pid           # Single-instance lock file (not committed)
└── .gitignore
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/shopify-order-alert-agent.git
cd shopify-order-alert-agent
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your environment variables

Copy the example below into a `.env` file in the project root:

```
SHOPIFY_STORE_URL=https://your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_shopify_access_token
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
CHECK_INTERVAL_MINUTES=1
MIN_ORDER_AMOUNT=250
```

| Variable | Description |
|---|---|
| `SHOPIFY_STORE_URL` | Your store's base URL (no trailing slash) |
| `SHOPIFY_ACCESS_TOKEN` | Private app access token from Shopify Admin |
| `SLACK_WEBHOOK_URL` | Incoming Webhook URL from your Slack app |
| `CHECK_INTERVAL_MINUTES` | How often to poll for new orders (in minutes) |
| `MIN_ORDER_AMOUNT` | Minimum order total in USD to trigger an alert |

#### Getting your Shopify Access Token
1. In Shopify Admin, go to **Settings → Apps and sales channels → Develop apps**
2. Create a private app and grant it `read_orders` permission under the Admin API scopes
3. Copy the generated access token

#### Getting your Slack Webhook URL
1. Go to [api.slack.com/apps](https://api.slack.com/apps) and create a new app
2. Enable **Incoming Webhooks** and add a webhook to your target channel
3. Copy the webhook URL

---

## Running the Agent

```bash
venv/bin/python main.py
```

The agent will:
1. Immediately run a baseline check to register all existing recent orders (no alerts sent)
2. Start polling every `CHECK_INTERVAL_MINUTES` and alert on any new qualifying orders

To stop the agent, press **Ctrl+C** in the terminal, or run:

```bash
pkill -f "main.py"
```

> **Note:** Only run one instance at a time. The agent enforces this with a PID lock file (`.agent.pid`). If you see `Agent already running`, either stop the existing process or delete the stale `.agent.pid` file if the previous run crashed.

---

## Known Limitations

### Customer name on Shopify development stores
Shopify development/demo stores strip all PII (names, emails) from REST API responses. As a result, the **Customer** field in Slack alerts will always show `Guest` when running against a development store, even if the customer record has a name and email in the Shopify admin.

On a real production store, the `customer.first_name`, `customer.last_name`, `billing_address.name`, and `order.email` fields are fully populated and the customer name will resolve correctly.

---

## Use Case

This agent is intentionally simple by design — a focused, single-purpose tool that is straightforward to extend. Below are two real-world directions it could grow in a production e-commerce context.

### Fraud Detection

High-value orders placed by guest customers with mismatched billing and shipping addresses are a common fraud signal. The agent could be extended to:

- Flag orders where the billing country differs from the shipping country
- Alert on multiple orders placed within minutes from the same IP address (available via Shopify's order `browser_ip` field)
- Detect orders where an expedited shipping method is chosen for a first-time guest — a known pattern in card testing attacks
- Route suspicious orders to a dedicated `#fraud-alerts` Slack channel with a different color or priority label, separate from normal order alerts

### VIP Customer Alerts

For stores with a loyalty or high-value customer segment, the agent could:

- Cross-reference the customer email or ID against a maintained VIP list
- Send a richer Slack notification that includes the customer's lifetime order count and total spend, pulled from the Shopify Customers API
- Alert the relevant account manager or sales rep directly via Slack DM instead of a shared channel
- Trigger a follow-up workflow — such as a thank-you gift or priority fulfillment flag — by calling an internal API or a tool like Zapier alongside the Slack notification

Both extensions require only changes to `shopify_client.py` (to fetch additional fields) and `slack_notifier.py` (to format richer messages), keeping the scheduling and state management in `main.py` untouched.

---

## License

MIT
