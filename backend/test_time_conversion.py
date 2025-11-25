import sys
sys.path.insert(0, '/Users/jaychauhan/Documents/GitHub/lifepilot/backend')

from app.models import _to_24h

# Test various formats
test_times = [
    "2:00 PM",
    "2:00PM",  # No space
    "14:00",   # Already 24h
    "5:00 PM",
    "10:00 AM"
]

print("Testing _to_24h function:")
for time in test_times:
    result = _to_24h(time)
    print(f"{time:15} -> {result}")
