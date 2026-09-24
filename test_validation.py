import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lambda"))
from validate_transform import validate

GOOD = {"event_id": "abc", "event_type": "order_placed", "user_id": 42,
        "timestamp": "2026-09-23T00:00:00Z"}

def test_valid_event_passes():
    ok, _ = validate(GOOD); assert ok

def test_missing_field_fails():
    ok, reason = validate({k: v for k, v in GOOD.items() if k != "user_id"})
    assert not ok and reason == "missing_field:user_id"

def test_unknown_event_type_fails():
    ok, reason = validate(dict(GOOD, event_type="hacked"))
    assert not ok and "unknown_event_type" in reason
