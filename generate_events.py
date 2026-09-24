"""Generate simulated e-commerce events and upload to S3 raw zone."""
import argparse, json, random, uuid, boto3
from datetime import datetime, timezone

TYPES = ["page_view", "add_to_cart", "checkout_start", "order_placed", "order_refunded"]

def make_event(anomalies=False):
    e = {"event_id": str(uuid.uuid4()),
         "event_type": random.choices(TYPES, weights=[60, 20, 10, 8, 2])[0],
         "user_id": random.randint(1, 200000),
         "item_id": random.randint(1, 5000),
         "timestamp": datetime.now(timezone.utc).isoformat()}
    if anomalies and random.random() < 0.01:
        e["event_type"] = random.choice(["", "UNKNOWN_EVENT"])
    return e

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--count", type=int, default=1_000_000)
    ap.add_argument("--key", default="events/batch.jsonl")
    ap.add_argument("--anomalies", action="store_true")
    args = ap.parse_args()
    body = "\n".join(json.dumps(make_event(args.anomalies)) for _ in range(args.count)).encode()
    boto3.client("s3").put_object(Bucket=args.bucket, Key=args.key, Body=body)
    print("uploaded {:,} events".format(args.count))

if __name__ == "__main__":
    main()
