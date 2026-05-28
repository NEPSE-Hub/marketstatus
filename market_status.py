from datetime import datetime, timezone, timedelta

# Add market holidays here manually
# Format: YYYY-MM-DD
HOLIDAYS = {
    "2026-05-28",
    "2026-05-29",
}


def get_market_status():
    # Nepal Standard Time (NPT) is UTC +5:45
    npt_tz = timezone(timedelta(hours=5, minutes=45))
    now = datetime.now(npt_tz)

    current_date = now.strftime("%Y-%m-%d")

    # Monday = 0
    # Friday = 4
    # Saturday = 5
    # Sunday = 6

    weekday = now.weekday()

    # Market open days
    market_days = [0, 1, 2, 3, 4]

    # Check holiday
    if current_date in HOLIDAYS:
        return {
            "status": "market close"
        }

    # Weekend check
    if weekday not in market_days:
        return {
            "status": "market close"
        }

    # Market timing
    current_minutes = now.hour * 60 + now.minute

    market_open = 11 * 60
    market_close = 15 * 60

    if market_open <= current_minutes < market_close:
        return {
            "status": "market open"
        }

    return {
        "status": "market close"
    }