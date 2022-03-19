#!/usr/bin/python
import logging
import time
from typing import List
from dateutil import tz
from icalevents.icalevents import events
from icalevents.icalparser import Event
from settings import WEBDAV_CALENDAR_URL, WEBDAV_IS_APPLE


logger = logging.getLogger('app')


def sort_by_date(e: Event):
    return e.start.astimezone()


def get_events(max_number: int) -> List[Event]:
    logger.info("calendar_module.get_events(); trying....")
    utc_timezone = tz.tzutc()
    current_timezone = tz.tzlocal()

    try:
        event_list = events(WEBDAV_CALENDAR_URL, fix_apple=WEBDAV_IS_APPLE)
        event_list.sort(key=sort_by_date)

        start_count = 0
        for event in event_list:
            event.start.replace(tzinfo=utc_timezone)
            event.start = event.start.astimezone(current_timezone)

            # remove events from previous day (problem based on time-zones)
            day_number = time.localtime().tm_mday
            event_date = event.start.date()
            if day_number == 1 and event_date.month < time.localtime().tm_mon:
                start_count += 1
                max_number += 1
            elif event_date.day < day_number:
                start_count += 1
                max_number += 1

        logger.info("calendar_module.get_events(); got {} entries (capped to {}).".format(
            len(event_list), max_number-start_count))
        return event_list[start_count:max_number]

    except Exception as e:
        logger.critical(e)
        return None

