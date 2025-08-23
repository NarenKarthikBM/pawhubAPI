from datetime import date, datetime


def serialize_datetime(obj: datetime | date | str | None) -> str:
    if not obj:
        return ""
    return obj if isinstance(obj, str) else obj.isoformat()


def parse_datetime(string: str | None) -> datetime:
    if not string:
        return datetime.min
    return datetime.fromisoformat(string)


def is_time_format(input: str):
    try:
        datetime.strptime(input, "%H:%M")
        return True
    except ValueError:
        return False
