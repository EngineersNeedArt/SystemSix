#!/usr/bin/python
import logging
import lib.epd5in83_V2 as eInk


logger = logging.getLogger('app')


def init_display(epd: eInk.EPD):
    logger.info("Init display")
    epd.init()


def clear_display(epd: eInk.EPD):
    logger.info("Clear display")
    epd.Clear()


def set_sleep(epd: eInk.EPD):
    logger.info("Set display to sleep-mode")
    epd.sleep()

