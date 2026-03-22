import re
from typing import Optional, Union

# convert time in seconds to a MM:SS.sss format

def format_time(seconds: Optional[float]) -> str:
  if seconds is None or seconds < 0:
    return "N/A"
  minutes = int(seconds // 60)
  secs = seconds % 60
  return f"{minutes:02}:{secs:06.3f}"

def parse_time_string(time_str: Union[str, float, int, None]) -> Optional[float]:
  """
  Parse strings like:
    - "00:01:26:123000"
    - "00:01:26.123000"
    - "01:26.123"
    - "01:26"
  and return total seconds as float. Returns None if parsing fails.
  """
  # Handle timedelta format like "0 days 00:01:27.060000"
  if "days" in str(time_str):
    time_str_str: str = str(time_str).split(" ", 2)[-1]  # Take the time part after "X days "
  else:
    time_str_str: str = str(time_str).split(" ")[0]  # Remove any trailing text after space
    
  if time_str_str is None:
    print('1parse_time_string output: None')
    return None
  
  s: str = str(time_str_str).strip()
  if s == "":
    print('2parse_time_string output: None')
    return None

  # Split on colon or dot
  parts: list[str] = re.split(r'[:.]', s)
  # Normalize to hh, mm, ss, micro
  hh: int = 0
  micro: int = 0

  try:
    if len(parts) == 4:
      hh_str, mm_str, ss_str, micro_str = parts
      hh, mm, ss = int(hh_str), int(mm_str), int(ss_str)
      micro = int(str(micro_str)[:6].ljust(6, '0'))
    elif len(parts) == 3:
      # Ambiguity: could be HH:MM:SS OR MM:SS:micro
      # Decide by examining the last part length: if > 2 digits it's probably microseconds
      if len(parts[2]) > 2:
        mm_str, ss_str, micro_str = parts
        mm, ss = int(mm_str), int(ss_str)
        micro = int(str(micro_str)[:6].ljust(6, '0'))
      else:
        hh_str, mm_str, ss_str = parts
        hh, mm, ss = int(hh_str), int(mm_str), int(ss_str)
    elif len(parts) == 2:
      mm_str, ss_str = parts
      mm, ss = int(mm_str), int(ss_str)
    else:
      print('3parse_time_string output: None')
      return None

    total_seconds: float = hh * 3600 + mm * 60 + ss + micro / 1_000_000.0

    return round(total_seconds, 3)
  except Exception as e:
    print('Exception in parse_time_string:', e)
    print('4parse_time_string output: None')
    return None
