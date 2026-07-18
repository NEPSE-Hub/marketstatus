from datetime import datetime, timezone, timedelta

# Add market holidays here manually
# Format: YYYY-MM-DD
HOLIDAYS = {
    "2026-05-28",
    "2026-05-29",
    "2026-08-28",
    "2026-09-04",
    "2026-09-14",
    "2026-09-25",
    "2026-10-19",
    "2026-10-20",
    "2026-10-21",
    "2026-10-22",
    "2026-10-23",
    "2026-11-09",
    "2026-11-10",
    "2026-11-11",
    "2026-11-12",
    "2026-11-24",
    "2026-12-03",
    "2026-12-04",
}


def get_last_trading_day(reference_date: datetime) -> datetime:
    """Return the last trading day (previous market day) at 15:00 NPT."""
    npt_tz = timezone(timedelta(hours=5, minutes=45))
    one_day = timedelta(days=1)

    current = reference_date.replace(hour=15, minute=0, second=0, microsecond=0)
    # Ensure we don't count the reference date itself if it's a trading day but before close. For as_of after close, we want the same day's close? Actually no: if today is trading day
    # and it's after 15:00, the last trading day is today. But user wants "last trading date and time" when market close after 15:00. That could be today at 15:00. But careful: if today is holiday/weekend,
    # we need to go back. We'll implement general: find previous date that is a market day. Start from reference_date - 1 day.
    check_date = reference_date - one_day
    while True:
        check_date_str = check_date.strftime("%Y-%m-%d")
        weekday = check_date.weekday()
        if weekday in [0,1,2,3,4] and check_date_str not in HOLIDAYS:
            # Trading day found
            return check_date.replace(hour=15, minute=0, second=0, microsecond=0)
        check_date -= one_day

def get_market_status():
    # Nepal Standard Time (NPT) is UTC +5:45
    npt_tz = timezone(timedelta(hours=5, minutes=45))
    now = datetime.now(npt_tz)

    current_date = now.strftime("%Y-%m-%d")
    weekday = now.weekday()

    market_days = [0, 1, 2, 3, 4]  # Mon-Fri

    # NEW: Today status
    today_status = (
        "close"
        if current_date in HOLIDAYS or weekday not in market_days
        else "open"
    )

    # Helper to get current time in minutes
    current_minutes = now.hour * 60 + now.minute

    # Define time slots
    pre_open_start = 10 * 60 + 30      # 10:30
    pre_open_special_end = 10 * 60 + 44  # 10:44:59
    pre_open_matching_start = 10 * 60 + 45  # 10:45
    pre_open_matching_end = 10 * 60 + 59  # 10:59:59
    market_open_start = 11 * 60        # 11:00
    market_open_end = 15 * 60 - 1      # 14:59:59
    market_close_from = 15 * 60        # 15:00

    # Determine status
    status = None
    is_open_session = False

    # Holiday or weekend -> closed all day
    if current_date in HOLIDAYS or weekday not in market_days:
        status = "market close"
        is_open_session = False
    else:
        # Trading day logic
        if current_minutes < pre_open_start:
            status = "market close"
            is_open_session = False
        elif current_minutes <= pre_open_special_end:
            status = "Pre-open/Special Pre-open"
            is_open_session = True
        elif current_minutes <= pre_open_matching_end:
            status = "Pre-open matching"
            is_open_session = True
        elif current_minutes <= market_open_end:
            status = "market open"
            is_open_session = True
        else:
            status = "market close"
            is_open_session = False

    # Determine as_of
    if is_open_session:
        as_of = now
    else:
        as_of = get_last_trading_day(now)

    return {
        "today": today_status,   # NEW JSON RESPONSE
        "status": status,
        "as_of": as_of.strftime("%Y-%m-%d %H:%M:%S %Z")
    }