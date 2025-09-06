from datetime import datetime, timezone

def utc_now():
    """Return current UTC datetime"""
    return datetime.now(timezone.utc)

def parse_datetime(date_string):
    """Parse ISO datetime string and ensure UTC timezone"""
    if not date_string:
        return None
    dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)

def format_datetime(dt):
    """Format datetime as ISO string with UTC timezone"""
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()