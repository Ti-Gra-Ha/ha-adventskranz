"""Constants and date calculation for the Adventskranz integration."""
from __future__ import annotations

from datetime import date, timedelta
from typing import TypedDict

DOMAIN = "adventskranz"
PLATFORMS = ["sensor", "select", "date"]


class PhaseInfo(TypedDict):
    phase: int
    key: str
    label: str
    short_label: str
    candles_lit: int
    burned_down: bool
    default_image: str


PHASES: dict[int, PhaseInfo] = {
    0: {
        "phase": 0,
        "key": "new_candles",
        "label": "4 neue Kerzen (Vor dem 1. Advent)",
        "short_label": "Vor dem 1. Advent",
        "candles_lit": 0,
        "burned_down": False,
        "default_image": "/local/adventskranz/advent_0.png",
    },
    1: {
        "phase": 1,
        "key": "advent_1",
        "label": "1. Advent (1 brennende Kerze)",
        "short_label": "1. Advent",
        "candles_lit": 1,
        "burned_down": False,
        "default_image": "/local/adventskranz/advent_1.png",
    },
    2: {
        "phase": 2,
        "key": "advent_2",
        "label": "2. Advent (2 brennende Kerzen)",
        "short_label": "2. Advent",
        "candles_lit": 2,
        "burned_down": False,
        "default_image": "/local/adventskranz/advent_2.png",
    },
    3: {
        "phase": 3,
        "key": "advent_3",
        "label": "3. Advent (3 brennende Kerzen)",
        "short_label": "3. Advent",
        "candles_lit": 3,
        "burned_down": False,
        "default_image": "/local/adventskranz/advent_3.png",
    },
    4: {
        "phase": 4,
        "key": "advent_4",
        "label": "4. Advent (4 brennende Kerzen)",
        "short_label": "4. Advent",
        "candles_lit": 4,
        "burned_down": False,
        "default_image": "/local/adventskranz/advent_4.png",
    },
    5: {
        "phase": 5,
        "key": "burned_down",
        "label": "4 abgebrannte Kerzen (Nach dem 4. Advent)",
        "short_label": "Nach dem 4. Advent",
        "candles_lit": 0,
        "burned_down": True,
        "default_image": "/local/adventskranz/advent_5.png",
    },
}


def calculate_advent_dates(year: int) -> dict[str, date]:
    """Calculate the 4 Advent Sundays and the Sunday after 4th Advent for a given year.

    4th Advent is the Sunday on or before December 24 (falls between Dec 18 and Dec 24).
    """
    dec24 = date(year, 12, 24)
    # isoweekday(): Monday=1 .. Sunday=7 -> % 7 gives Sunday=0, Monday=1 .. Saturday=6
    days_since_sunday = dec24.isoweekday() % 7
    advent_4 = dec24 - timedelta(days=days_since_sunday)
    advent_3 = advent_4 - timedelta(days=7)
    advent_2 = advent_4 - timedelta(days=14)
    advent_1 = advent_4 - timedelta(days=21)
    sunday_after_advent_4 = advent_4 + timedelta(days=7)

    return {
        "advent_1": advent_1,
        "advent_2": advent_2,
        "advent_3": advent_3,
        "advent_4": advent_4,
        "sunday_after_advent_4": sunday_after_advent_4,
    }


def get_phase_for_date(target_date: date) -> int:
    """Return the phase index (0..5) for the given date.

    - 0: 01.01. until day before 1st Advent (4 neue Kerzen)
    - 1: from 1st Advent (1 brennende Kerze)
    - 2: from 2nd Advent (2 brennende Kerzen)
    - 3: from 3rd Advent (3 brennende Kerzen)
    - 4: from 4th Advent (4 brennende Kerzen)
    - 5: from Sunday after 4th Advent through 31.12. (4 abgebrannte Kerzen)
    """
    dates = calculate_advent_dates(target_date.year)
    if target_date >= dates["sunday_after_advent_4"]:
        return 5
    if target_date >= dates["advent_4"]:
        return 4
    if target_date >= dates["advent_3"]:
        return 3
    if target_date >= dates["advent_2"]:
        return 2
    if target_date >= dates["advent_1"]:
        return 1
    return 0
