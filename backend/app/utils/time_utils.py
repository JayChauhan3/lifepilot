"""
Time utility functions for routine scheduling and conflict detection.
"""
from typing import Tuple, Optional
from datetime import datetime, timedelta


def parse_time_to_minutes(time_str: str) -> int:
    """
    Convert a time string to minutes since midnight.
    
    Accepts either 24h format (e.g. "14:30") or 12h format with AM/PM (e.g. "2:30 PM").
    """
    if time_str is None:
        raise ValueError("Invalid time format: None provided")
    
    normalized = time_str.strip()
    
    # Try 24-hour format first
    try:
        hours, minutes = map(int, normalized.split(':'))
        if 0 <= hours < 24 and 0 <= minutes < 60:
            return hours * 60 + minutes
    except (ValueError, AttributeError):
        pass
    
    # Fall back to 12-hour format with AM/PM
    try:
        dt = datetime.strptime(normalized.upper().replace('.', ''), '%I:%M %p')
        return dt.hour * 60 + dt.minute
    except ValueError:
        try:
            dt = datetime.strptime(normalized.upper().replace('.', ''), '%I:%M%p')
            return dt.hour * 60 + dt.minute
        except ValueError:
            raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM or HH:MM AM/PM")


def normalize_time_to_24h(time_str: str) -> str:
    """
    Normalize any supported time string to HH:MM (24h) format.
    """
    minutes = parse_time_to_minutes(time_str)
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def times_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    """
    Check if two time ranges overlap, handling overnight ranges.
    
    Args:
        start1: Start time of first range (24h format)
        end1: End time of first range (24h format)
        start2: Start time of second range (24h format)
        end2: End time of second range (24h format)
    
    Returns:
        True if the time ranges overlap, False otherwise
    
    Examples:
        >>> times_overlap("09:00", "17:00", "14:00", "18:00")  # Overlap
        True
        >>> times_overlap("09:00", "17:00", "18:00", "20:00")  # No overlap
        False
        >>> times_overlap("22:00", "06:00", "23:00", "01:00")  # Overnight overlap
        True
        >>> times_overlap("22:00", "06:00", "07:00", "09:00")  # No overlap with overnight
        False
    """
    s1 = parse_time_to_minutes(start1)
    e1 = parse_time_to_minutes(end1)
    s2 = parse_time_to_minutes(start2)
    e2 = parse_time_to_minutes(end2)
    
    # Check if either range is overnight (end < start)
    range1_overnight = e1 < s1
    range2_overnight = e2 < s2
    
    if not range1_overnight and not range2_overnight:
        # Both ranges are within the same day
        # Overlap if: start1 < end2 AND start2 < end1
        return s1 < e2 and s2 < e1
    
    elif range1_overnight and not range2_overnight:
        # Range 1 is overnight, range 2 is not
        # Range 1 covers [s1, 1440) and [0, e1)
        # Overlap if range 2 intersects either part
        return (s2 < e1) or (s1 < e2)
    
    elif not range1_overnight and range2_overnight:
        # Range 2 is overnight, range 1 is not
        # Range 2 covers [s2, 1440) and [0, e2)
        # Overlap if range 1 intersects either part
        return (s1 < e2) or (s2 < e1)
    
    else:
        # Both ranges are overnight
        # They will always overlap since both span midnight
        return True


def format_time_range(start: str, end: str) -> str:
    """
    Format a time range for display.
    
    Args:
        start: Start time in 24h format
        end: End time in 24h format
    
    Returns:
        Formatted string like "9:00 AM - 5:00 PM"
    """
    def to_12h(time_24: str) -> str:
        try:
            time_obj = datetime.strptime(time_24, '%H:%M')
            return time_obj.strftime('%-I:%M %p')
        except (ValueError, TypeError):
            return time_24
    
    return f"{to_12h(start)} - {to_12h(end)}"


def get_available_slots(
    occupied_ranges: list[Tuple[str, str]], 
    min_duration_minutes: int = 60
) -> list[Tuple[str, str]]:
    """
    Find available time slots given a list of occupied time ranges.
    
    Args:
        occupied_ranges: List of (start, end) tuples in 24h format
        min_duration_minutes: Minimum duration for a slot to be considered available
    
    Returns:
        List of available (start, end) tuples
    
    Example:
        >>> occupied = [("09:00", "12:00"), ("14:00", "17:00")]
        >>> get_available_slots(occupied, 60)
        [("00:00", "09:00"), ("12:00", "14:00"), ("17:00", "23:59")]
    """
    if not occupied_ranges:
        return [("00:00", "23:59")]
    
    # Convert to minutes and sort
    occupied_minutes = [
        (parse_time_to_minutes(start), parse_time_to_minutes(end))
        for start, end in occupied_ranges
    ]
    occupied_minutes.sort()
    
    available = []
    current_time = 0  # Start of day
    
    for start, end in occupied_minutes:
        # Check if there's a gap before this occupied range
        if start - current_time >= min_duration_minutes:
            available.append((
                f"{current_time // 60:02d}:{current_time % 60:02d}",
                f"{start // 60:02d}:{start % 60:02d}"
            ))
        current_time = max(current_time, end)
    
    # Check for gap at end of day
    end_of_day = 23 * 60 + 59
    if end_of_day - current_time >= min_duration_minutes:
        available.append((
            f"{current_time // 60:02d}:{current_time % 60:02d}",
            "23:59"
        ))
    
    return available
