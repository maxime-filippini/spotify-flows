# Standard library imports
from datetime import datetime

# Third party imports

# Local imports

# Main body
def date_parsing(date_str: str) -> datetime:
    """Parse string of varying length to datetime object

    Args:
        date_str (str): Input date string

    Returns:
        datetime: Output datetime object
    """
    if len(date_str) == 4:
        return datetime(int(date_str), 1, 1)
    elif len(date_str) == 10:
        return datetime.strptime(date_str, "%Y-%m-%d")
    else:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
