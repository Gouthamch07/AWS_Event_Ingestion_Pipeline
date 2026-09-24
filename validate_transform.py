"""SQS-triggered Lambda: validate, route valid -> curated, invalid -> quarantine + alert."""
import json, os, boto3

s3 = boto3.client("s3"); sns = boto3.client("sns")
CURATED = os.environ["CURATED_BUCKET"]; QUARANTINE = os.environ["QUARANTINE_BUCKET"]
ALERT_TOPIC = os.environ["ALERT_TOPIC"]
VALID = {"page_view", "add_to_cart", "checkout_start", "order_placed", "order_refunded"}
REQUIRED = {"event_id": str, "event_type": str, "user_id": int, "timestamp": str}

def validate(e):
    for f, t in REQUIRED.items():
        if f not in e or e[f] is None: return False, "missing_field:" + f
        if not isinstance(e[f], t): return False, "bad_type:" + f
    if e["event_type"] not in VALID: return False, "unknown_event_type"
    return True, None

def handler(records, context):
    valid, invalid = [], []
    for r in records["Records"]:
        for line in r["body"].splitlines():
            try: e = json.loads(line)
            except json.JSONDecodeError:
                invalid.append((line, "unparseable_json")); continue
            ok, reason = validate(e)
            (valid if ok else invalid).append(e if ok else (line, reason))
    stamp = context.aws_request_id
    if valid:
        s3.put_object(Bucket=CURATED, Key="events/" + stamp + ".jsonl",
                      Body="\n".join(json.dumps(x) for x in valid).encode())
    if invalid:
        s3.put_object(Bucket=QUARANTINE, Key="events/" + stamp + ".jsonl",
                      Body="\n".join(json.dumps({"raw": a, "reason": b}) for a, b in invalid).encode())
        sns.publish(TopicArn=ALERT_TOPIC, Subject="Quarantined {} events".format(len(invalid)),
                    Message="Batch {}: {}/{} invalid".format(stamp, len(invalid), len(valid) + len(invalid)))
    return {"valid": len(valid), "quarantined": len(invalid)}
