# app/tools.py

from datetime import datetime
from zoneinfo import ZoneInfo

def get_current_time(timezone: str) -> dict:
    time_zone_info = datetime.now(ZoneInfo(timezone))
    time_zone_name = time_zone_info.tzname()

    return {
        "time": f"{time_zone_info}",
        "timezone": f"{time_zone_name}"
    }
    

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the EXACT current time for a given timezone. Always use this tool when asked about current time - never guess.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {"type": "string", "description": "time zone name"}
                },
                "required": ["timezone"]
            }
        }
    }
]

TOOL_MAP = {
    "get_current_time": get_current_time
}