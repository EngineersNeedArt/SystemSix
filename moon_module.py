#!/usr/bin/python
"""Functions for calculating moon phase."""

import datetime
import math
import sys
import collections


def get_moon_phase(date):
    """
    Get decimal moon phase for a date.
    Date should be in the format YYYY-MM-DD.
    Returns the day of the lunar cycle (0-29).
    Algorithm influenced by Ben Daglish:
    http://www.ben-daglish.net/moon.shtml
    """
    phase_len = 2551443
    year, month, day = date.split("-", 2)
    epoch = datetime.datetime(1970, 1, 1)
    new_moon = (datetime.datetime(1970, 1, 7) - epoch).total_seconds()
    user_date = (datetime.datetime(int(year), int(month), int(day)) - epoch).total_seconds()
    phase = (user_date - new_moon) % phase_len
    
    return math.floor(phase / (24 * 3600) + 1)
    

def interpret_moon_phase(phase):
    """Translate phase into common language for moon phases."""
    if phase == 0 or phase == 30:
        return "New Moon"
    if phase > 0 and phase < 7.5:
        return "Waxing Crescent"
    if phase > 7.5 and phase < 15:
        return "Waxing Gibbous"
    if phase == 15:
        return "Full Moon"
    if phase > 15 and phase < 22.5:
        return "Waning Gibbous"
    if phase > 22.5 and phase < 30:
        return "Waning Crescent"


def get_next_phase(phase):
    """Get next full or new moon time."""
    if phase == 0 or phase == 30 or phase == 15:
        return None
    NextPhase = collections.namedtuple("NextPhase", ["next_phase", "days"])
    if phase < 15:
        NextPhase.days = int(15 - phase)
        NextPhase.next_phase = "Full Moon"
        return NextPhase
    if phase < 30:
        NextPhase.days = int(30 - phase)
        NextPhase.next_phase = "New Moon"
        return NextPhase


def main():
    """Run program if called directly."""
    if len(sys.argv) == 2:
        user_date = sys.argv[1]
    else:
        now = datetime.datetime.now()
        user_date = (str(now.year) + "-" + str(now.month).zfill(2) + "-" + str(now.day).zfill(2))
    phase = get_moon_phase(user_date)
    print(user_date + ": " + interpret_moon_phase(phase) + " (" + str(phase) + " days into cycle)")
    NextPhase = get_next_phase(phase)
    if NextPhase:
        print(NextPhase.next_phase + " in " + str(NextPhase.days) + " days.")

if __name__ == "__main__":
    main()