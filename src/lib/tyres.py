from typing import Dict, Optional

tyre_compounds_ints: Dict[str, int] = {
  "SOFT": 0,
  "MEDIUM": 1,
  "HARD": 2,
  "INTERMEDIATE": 3,
  "WET": 4,
}

def get_tyre_compound_int(compound_str: str) -> int:
  return int(tyre_compounds_ints.get(compound_str.upper(), -1))

def get_tyre_compound_str(compound_int: int) -> str:
  for k, v in tyre_compounds_ints.items():
    if v == compound_int:
      return k
  return "UNKNOWN"