from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from shopify_client import get_recent_orders
from slack_notifier import send_order_alert
import os
import sys
import json
import atexit

load_dotenv()

CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", 1))
MIN_ORDER_AMOUNT = float(os.getenv("MIN_ORDER_AMOUNT", 250))
STATE_FILE = ".state.json"
PID_FILE = ".agent.pid"


def acquire_lock():
    try:
        with open(PID_FILE, "x") as f:  # atomic exclusive create
            f.write(str(os.getpid()))
    except FileExistsError:
        with open(PID_FILE) as f:
            old_pid = int(f.read().strip())
        try:
            os.kill(old_pid, 0)
            print(f"Agent already running (PID {old_pid}). Stop it first with: kill {old_pid}")
            sys.exit(1)
        except ProcessLookupError:
            os.remove(PID_FILE)  # stale lock, retry
            acquire_lock()
    atexit.register(lambda: os.path.exists(PID_FILE) and os.remove(PID_FILE))


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            data = json.load(f)
            return data.get("last_seen_id"), set(data.get("notified_ids", []))
    return None, set()


def save_state(last_seen_id, notified_ids):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_seen_id": last_seen_id, "notified_ids": list(notified_ids)}, f)


def check_new_orders():
    last_seen_id, notified_ids = load_state()
    orders = get_recent_orders(since_id=last_seen_id)
    if not orders:
        return

    max_id = max(o["id"] for o in orders)
    alerted = 0
    for order in reversed(orders):
        order_id = order["id"]
        if order_id in notified_ids:
            continue
        if float(order.get("total_price", 0)) >= MIN_ORDER_AMOUNT:
            send_order_alert(order)
            alerted += 1
        notified_ids.add(order_id)

    save_state(max_id, notified_ids)
    print(f"Fetched {len(orders)} order(s), alerted on {alerted} above ${MIN_ORDER_AMOUNT:.0f}. Last seen ID: {max_id}")


if __name__ == "__main__":
    acquire_lock()
    print(f"Starting Shopify order alert agent (PID {os.getpid()}, interval: {CHECK_INTERVAL_MINUTES}m)...")
    check_new_orders()

    scheduler = BlockingScheduler()
    scheduler.add_job(check_new_orders, "interval", minutes=CHECK_INTERVAL_MINUTES)
    scheduler.start()
