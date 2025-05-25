import datetime
import pytz


def get_greeting():
    """
    Returns a greeting based on the time of day
    
    Returns:
        str: A greeting message
    """
    current_hour = datetime.datetime.now().hour
    
    if 5 <= current_hour < 12:
        return "Добро утро!"
    elif 12 <= current_hour < 18:
        return "Добър ден!"
    elif 18 <= current_hour < 22:
        return "Добър вечер!"
    else:
        return "Здравейте!"


def get_formatted_time(timezone="Europe/Sofia"):
    """
    Returns the current time formatted as a string
    
    Args:
        timezone: The timezone to use (default: Europe/Sofia)
        
    Returns:
        str: The formatted time string
    """
    tz = pytz.timezone(timezone)
    now = datetime.datetime.now(tz)
    return now.strftime("%H:%M:%S")


def get_formatted_date(timezone="Europe/Sofia", include_weekday=True):
    """
    Returns the current date formatted as a string
    
    Args:
        timezone: The timezone to use (default: Europe/Sofia)
        include_weekday: Whether to include the day of the week
        
    Returns:
        str: The formatted date string
    """
    tz = pytz.timezone(timezone)
    now = datetime.datetime.now(tz)
    
    if include_weekday:
        # Bulgarian weekday names
        weekdays = {
            0: "понеделник",
            1: "вторник",
            2: "сряда",
            3: "четвъртък",
            4: "петък",
            5: "събота",
            6: "неделя",
        }
        weekday = weekdays.get(now.weekday(), "")
        return f"{now.strftime('%d.%m.%Y')} ({weekday})"
    else:
        return now.strftime("%d.%m.%Y")


def get_month_name(month_number, lang="bg"):
    """
    Returns the month name for a given month number
    
    Args:
        month_number: The month number (1-12)
        lang: The language code (default: bg for Bulgarian)
        
    Returns:
        str: The month name
    """
    if lang == "bg":
        months = {
            1: "януари",
            2: "февруари",
            3: "март",
            4: "април",
            5: "май",
            6: "юни",
            7: "юли",
            8: "август",
            9: "септември",
            10: "октомври",
            11: "ноември",
            12: "декември",
        }
    else:
        # Default to English
        months = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }
    
    return months.get(month_number, "") 