#!/usr/bin/python3
import locale
import random
import schedule
import time
USE_EINK_DISPLAY = True  # Set to False to (test) build on a machine without an e-ink display.
if USE_EINK_DISPLAY:
    import lib.epd5in83_V2 as eInk
    from eink_utils import *
from calendar_module import get_events
from desktop_render import *
from weather_module import get_weather_forecast
from settings import TRASH_DAY, LOCALE

DEBUG = False

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"),
                    handlers=[logging.FileHandler(filename="info.log", mode='w'), logging.StreamHandler()])
logger = logging.getLogger('app')

art_icons = ["icon_art0.bmp", "icon_art1.bmp", "icon_art2.bmp",
             "icon_art3.bmp", "icon_art4.bmp", "icon_art5.bmp",
             "icon_art6.bmp", "icon_art7.bmp", "icon_art8.bmp",
             "icon_art9.bmp"]

dev_icons = ["icon_dev0.bmp", "icon_dev1.bmp", "icon_dev2.bmp",
             "icon_dev3.bmp", "icon_dev4.bmp", "icon_dev5.bmp",
             "icon_dev6.bmp", "icon_dev7.bmp", "icon_dev8.bmp", 
             "icon_dev9.bmp"]

game_icons = ["icon_game0.bmp", "icon_game1.bmp", "icon_game2.bmp",
              "icon_game3.bmp", "icon_game4.bmp", "icon_game5.bmp",
              "icon_game6.bmp", "icon_game7.bmp", "icon_game8.bmp",
              "icon_game9.bmp", "icon_game10.bmp", "icon_game11.bmp",
              "icon_game12.bmp", "icon_game13.bmp", "icon_game14.bmp",
              "icon_game15.bmp", "icon_game16.bmp", "icon_game17.bmp",
              "icon_game18.bmp", "icon_game19.bmp", "icon_game20.bmp",
              "icon_game21.bmp", "icon_game22.bmp", "icon_game23.bmp",
              "icon_game24.bmp", "icon_game25.bmp", "icon_game26.bmp",
              "icon_game27.bmp", "icon_game28.bmp", "icon_game29.bmp",
              "icon_game30.bmp", "icon_game31.bmp", "icon_game32.bmp",
              "icon_game33.bmp", "icon_game34.bmp", "icon_game35.bmp",
              "icon_game36.bmp", "icon_game37.bmp", "icon_game38.bmp",
              "icon_game39.bmp", "icon_game40.bmp", "icon_game41.bmp",
              "icon_game42.bmp", "icon_game43.bmp", "icon_game44.bmp",
              "icon_game45.bmp", "icon_game46.bmp", "icon_game47.bmp",
              "icon_game48.bmp", "icon_game49.bmp", "icon_game50.bmp",
              "icon_game51.bmp", "icon_game52.bmp", "icon_game53.bmp",
              "icon_game54.bmp", "icon_game55.bmp", "icon_game56.bmp",
              "icon_game57.bmp", "icon_game58.bmp", "icon_game59.bmp",
              "icon_game60.bmp", "icon_game61.bmp", "icon_game62.bmp",
              "icon_game63.bmp", "icon_game64.bmp", "icon_game65.bmp",
              "icon_game66.bmp", "icon_game67.bmp", "icon_game68.bmp",
              "icon_game69.bmp", "icon_game70.bmp", "icon_game71.bmp",
              "icon_game72.bmp", "icon_game73.bmp", "icon_game74.bmp",
              "icon_game75.bmp", "icon_game76.bmp"]

office_icons = ["icon_office0.bmp", "icon_office1.bmp", "icon_office2.bmp",
                "icon_office3.bmp", "icon_office4.bmp", "icon_office5.bmp",
                "icon_office6.bmp", "icon_office7.bmp"]

system_icons = ["icon_sys0.bmp", "icon_sys1.bmp", "icon_sys2.bmp",
                "icon_sys3.bmp", "icon_sys4.bmp", "icon_sys5.bmp",
                "icon_sys6.bmp", "icon_sys7.bmp", "icon_sys8.bmp",
                "icon_sys9.bmp", "icon_sys10.bmp", "icon_sys11.bmp",
                "icon_sys12.bmp", "icon_sys13.bmp", "icon_sys14.bmp",
                "icon_sys15.bmp", "icon_sys16.bmp"]

util_icons = ["icon_util0.bmp", "icon_util1.bmp", "icon_util2.bmp",
              "icon_util3.bmp", "icon_util4.bmp", "icon_util5.bmp",
              "icon_util6.bmp", "icon_util7.bmp", "icon_util8.bmp",
              "icon_util9.bmp", "icon_util10.bmp"]

# Global variables.
today = None
weather_forecast = None
weather_succeeded = False
event_list = None
calendar_succeeded = False
layout_index = None
startup_flavor = 0
adornment_flavor = 0
window_flavor = 0
window_icons = None
accessory_index = 0
cursor_origin = None


def is_trash_day(day: datetime):
    if TRASH_DAY is None:
        return False
    elif day.isoweekday() == TRASH_DAY:
        return True
    else:
        return random.randrange(7) == 0


# Since game icons (for example) are in abundance, we want to show a Games window more often.
# Weighs the likelihood of a particular window flavor based on how many icons we have for it.

def weighted_random_window_flavor():
    icon_range =  len(art_icons) + len(dev_icons) + len(game_icons) + len(office_icons) + len(system_icons) + len(util_icons)
    random_index = random.randrange(icon_range)
    flavor = 0
    random_index -= len(art_icons)
    if random_index <= 0:
        return flavor
    flavor = 1
    random_index -= len(dev_icons)
    if random_index <= 0:
        return flavor
    flavor = 2
    random_index -= len(game_icons)
    if random_index <= 0:
        return flavor
    flavor = 3
    random_index -= len(office_icons)
    if random_index <= 0:
        return flavor
    flavor = 4
    random_index -= len(system_icons)
    if random_index <= 0:
        return flavor
    flavor = 5
    return flavor


def icon_list_for_index(index: int):
    if index == 0:
        return art_icons
    elif index == 1:
        return dev_icons
    elif index == 2:
        return game_icons
    elif index == 3:
        return office_icons
    elif index == 4:
        return system_icons
    else:
        return util_icons


def adornments_for_index(index: int):
    if index == 0:
        return ["cairo_0.bmp", "cairo_1.bmp"]
    elif index == 1:
        return ["cairo_3.bmp", "cairo_2.bmp"]
    elif index == 2:
        return ["cairo_4.bmp", "cairo_4.bmp"]
    elif index == 3:
        return ["cairo_5.bmp", "cairo_6.bmp"]
    else:
        return ["cairo_7.bmp", "cairo_8.bmp"]


def new_layout_a():
    global startup_flavor
    global adornment_flavor
    global window_flavor
    global window_icons
    global accessory_index
    global cursor_origin

    startup_flavor = random.randrange(2)
    adornment_flavor = random.randrange(5)
    window_flavor = weighted_random_window_flavor()
    window_icons = random.sample(icon_list_for_index(window_flavor), 6)
    accessory_index = random.randrange(2)
    cursor_origin = (random.randrange(610) + 20, random.randrange(434) + 16)


def new_layout_b():
    global startup_flavor
    global adornment_flavor
    global accessory_index
    global cursor_origin

    startup_flavor = random.randrange(2)
    adornment_flavor = random.randrange(5)
    accessory_index = random.randrange(2)
    cursor_origin = (random.randrange(610) + 20, random.randrange(434) + 16)


def new_layout_c():
    global startup_flavor
    global adornment_flavor
    global window_icons
    global window_flavor
    global cursor_origin

    startup_flavor = random.randrange(2)
    adornment_flavor = random.randrange(5)
    window_flavor = weighted_random_window_flavor()
    window_icons = random.sample(icon_list_for_index(window_flavor), 6)
    cursor_origin = (random.randrange(610) + 20, random.randrange(434) + 16)


def render_layout_a(ink_draw: ImageDraw, ink_image: Image, day: datetime, period: str):
    global weather_forecast
    global event_list
    global startup_flavor
    global adornment_flavor
    global window_flavor
    global window_icons
    global accessory_index
    global cursor_origin

    # Draw the desktop.
    draw_desktop(ink_image, "desktop_plain.bmp")

    # Draw the start-up disk.
    if startup_flavor == 0:
        draw_startup_disk(ink_image, True)
    else:
        draw_startup_disk(ink_image, False)

    # Draw the trash can.
    draw_trash(ink_image, is_trash_day(day))

    # Draw a window with icons (3 x 2 icons).
    draw_3_2_window(ink_image, (400, 92), window_flavor, window_icons, False)

    # Draw the Scrapbook with weather data.
    date_str = datetime.strftime(day, "%A, %B %-d, %Y")
    adornments = adornments_for_index(adornment_flavor)
    draw_scrapbook(ink_draw, ink_image, (24, 40), date_str, adornments, weather_forecast, False)

    # Display Calendar data in a window in list view (maximum of 6 rows).
    draw_list_window(ink_draw, ink_image, (165, 288), event_list)

    # Optionally display the Moon desk accessory.
    if not handle_display_moon(ink_image, (32, 322), day, period):
        if accessory_index == 0:
            draw_puzzle_da(ink_image, (32, 332))
        else:
            draw_calculator_da(ink_image, (32, 292))

    # Cursor is displayed last, on top of everything else.
    draw_arrow_cursor(ink_image, cursor_origin)

    # Draw bezel last to "crop" any content hanging outside desktop.
    draw_image_plus_mask(ink_image, "bezel.bmp", "bezel_mask.bmp", (0, 0))


def render_layout_b(ink_draw: ImageDraw, ink_image: Image, day: datetime, period: str):
    global weather_forecast
    global event_list
    global startup_flavor
    global accessory_index
    global cursor_origin

    # Draw the desktop.
    draw_desktop(ink_image, "desktop_plain.bmp")

    # Draw the start-up disk.
    if startup_flavor == 0:
        draw_startup_disk(ink_image, True)
    else:
        draw_startup_disk(ink_image, False)

    # Draw the trash can.
    draw_trash(ink_image, is_trash_day(day))

    # Draw paint window.
    date_str = datetime.strftime(day, "%A, %B %-d, %Y")
    draw_paint_window(ink_draw, ink_image, date_str)

    # Draw the Scrapbook with weather data.
    draw_scrapbook(ink_draw, ink_image, (240, 90), None, None, weather_forecast, False)

    # Display Calendar data in a window in list view (maximum of 6 rows).
    draw_list_window(ink_draw, ink_image, (34, 330), event_list)

    # Optionally display the Moon desk accessory.
    if not handle_display_moon(ink_image, (450, 330), day, period):
        if accessory_index == 0:
            draw_puzzle_da(ink_image, (450, 332))
        else:
            draw_calculator_da(ink_image, (450, 292))

    # Cursor is displayed on top of everything else.
    draw_arrow_cursor(ink_image, cursor_origin)

    # Draw bezel last to "crop" any content hanging outside desktop.
    draw_image_plus_mask(ink_image, "bezel.bmp", "bezel_mask.bmp", (0, 0))


def render_layout_c(ink_draw: ImageDraw, ink_image: Image, day: datetime, period: str):
    global weather_forecast
    global event_list
    global startup_flavor
    global window_flavor
    global window_icons
    global accessory_index
    global cursor_origin

    # Draw the desktop.
    draw_desktop(ink_image, "desktop_plain.bmp")

    # Draw the start-up disk.
    if startup_flavor == 0:
        draw_startup_disk(ink_image, True)
    else:
        draw_startup_disk(ink_image, False)

    # Draw the trash can.
    draw_trash(ink_image, is_trash_day(day))

    # Draw a window with icons (3 x 2 icons).
    draw_3_2_window(ink_image, (406, 226), window_flavor, window_icons, False)

    # Draw write window.
    date_str = datetime.strftime(day, "%A, %B %-d, %Y")
    draw_write_window(ink_draw, ink_image, date_str, weather_forecast, False)

    # Display Calendar data in a window in list view (maximum of 6 rows).
    draw_list_window(ink_draw, ink_image, (34, 306), event_list)

    # Optionally display the Moon desk accessory.
    handle_display_moon(ink_image, (506, 92), day, period)

    # Cursor is displayed on top of everything else.
    draw_arrow_cursor(ink_image, cursor_origin)

    # Draw bezel last to "crop" any content hanging outside desktop.
    draw_image_plus_mask(ink_image, "bezel.bmp", "bezel_mask.bmp", (0, 0))


def update_display(period: str):
    global today
    logger.info("systemsix.update_display(); updating display.")

    try:
        # Prepare image and drawing context.
        ink_image = Image.open(os.path.join(ARTWORK_DIR, "blank.bmp"))
        ink_draw = ImageDraw.Draw(ink_image)

        # Render the Desktop to image.
        if layout_index == 0:
            render_layout_a(ink_draw, ink_image, today, period)
        elif layout_index == 1:
            render_layout_b(ink_draw, ink_image, today, period)
        elif layout_index == 2:
            render_layout_c(ink_draw, ink_image, today, period)

        # Display the final image on e-ink display.
        if USE_EINK_DISPLAY:
            logger.info("systemsix.update_display(); writing to display.")
            epd = eInk.EPD()
            init_display(epd)
            epd.display(epd.getbuffer(ink_image))
            set_sleep(epd)
        else:
            ink_image.save("INK_EXPORT.bmp")
            final_image = Image.open("INK_EXPORT.bmp")
            final_image.show()
        
    except Exception as e:
        logger.warning(e)
        if not DEBUG:
            logger.info("systemsix.update_display(); trying to module_exit().")
            if USE_EINK_DISPLAY:
                eInk.epdconfig.module_exit()
        raise e


def new_weather():
    global weather_forecast
    global weather_succeeded

    # Get weather forecast for the day (we do this only in the morning).
    weather_forecast = get_weather_forecast()

    # Validate weather forecast results. BOGUS: I often see an errant New Years forecast. Check for that.
    if (weather_forecast is None) or (len(weather_forecast) < 1):
        weather_succeeded = False
        logger.info("systemsix.new_layout(); failed to fetch weather forecast.")
    else:
        tomorrow_forecast_date = datetime.strptime(weather_forecast[2]['startTime'], '%Y-%m-%dT%H:%M:%S%z')
        aware_now = datetime.now(tomorrow_forecast_date.tzinfo)
        if tomorrow_forecast_date < aware_now:
            weather_forecast = None
            weather_succeeded = False
            logger.warning("systemsix.new_layout(); BOGUS weather forecast.")
        else:
            weather_succeeded = True
            logger.info("systemsix.new_layout(); fetch weather forecast successful.")


def new_calendar():
    global event_list
    global calendar_succeeded

    # Get calendar events for the day.
    event_list = get_events(6)
    if event_list is None:
        logger.warning("systemsix.new_layout(); failed to get calendar events.")
        calendar_succeeded = False
    else:
        logger.info("systemsix.new_layout(); fetch calendar events successful.")
        calendar_succeeded = True


def new_layout():
    global layout_index

    # Choose a new random layout for the day (some layouts are less freqent).
    layout = random.randrange(7)
    if layout == 0:
        layout_index = 1
    elif layout == 1:
        layout_index = 2
    else:
        layout_index = 0
    # layout_index = 2

    # Create all the random elements in new_layout_x(); only done in the morning.
    # Later calls to update_display() will not re-randomize the layout.
    if layout_index == 0:
        new_layout_a()
    elif layout_index == 1:
        new_layout_b()
    elif layout_index == 2:
        new_layout_c()


def period_for_hour(hour: int):
    # Find the period we have started within.
    if hour == 0:
        return "MIDNIGHT"
    elif hour == 4:
        return "MORNING"
    elif hour == 17:
        return "EVENING"
    else:
        return None


def nearest_period_for_hour(hour: int):
    # Find the period we have started within.
    if hour < 4:
        return "MIDNIGHT"
    elif hour < 17:
        return "MORNING"
    else:
        return "EVENING"


"""
All the "smart code" is in here to determine what to refresh and when based on three 'periods' of the day.
MIDNIGHT we refresh the display to how the new calendar date, we also try to refresh the weather.
MORNING we refresh the calendar and choose a new desktop layout. We then refresh the display.
EVENING we refresh the calendar again (tomorrow's events) and refresh the display.
Every hour we re-try fetching both the calendar and weather events if they had failed earlier. We refresh if needed.
The desktop layouts may display differently for the period, like show the Moon desk accessory in the evening.
Generally though we try not to frequently refresh the display as it looks poor when it flashes.  
"""


def update_or_start(start: bool = False):
    global today
    global weather_succeeded
    global calendar_succeeded

    # Get the hour, we'll do the appropriate update based on the hour.
    today = datetime.now()
    hour = today.hour
    logger.info('systemsix.update_or_start(); update hour: {}.'.format(hour))

    do_weather = False
    retry_weather = False
    do_calendar = False
    retry_calendar = False
    do_new_layout = False
    do_update_display = False

    # Handle data updates in case of previous failures.
    if (not start) and (not weather_succeeded):
        do_weather = True
        retry_weather = True

    if (not start) and (not calendar_succeeded):
        do_calendar = True
        retry_calendar = True

    # Special case when we first start SystemSix. Need to initialize a new layout, need all the data.
    if start:
        do_weather = True
        do_calendar = True
        do_new_layout = True
        period = nearest_period_for_hour(hour)
    else:
        period = period_for_hour(hour)

    # Update is based on the period ("MORNING" sees the most change).
    if period == "MIDNIGHT":
        do_update_display = True
    elif period == "MORNING":
        do_weather = True
        do_calendar = True
        do_new_layout = True
        do_update_display = True
    elif period == "EVENING":
        do_calendar = True
        do_update_display = True
    else:
        if do_weather or do_calendar:
            period = nearest_period_for_hour(hour)
        else:
            logger.info("systemsix.update_or_start(); nothing to update.")

    if do_weather:
        new_weather()
        if retry_weather and weather_succeeded:
            do_update_display = True
            logger.info("systemsix.update_or_start(); got weather this time.")

    if do_calendar:
        new_calendar()
        if retry_calendar and calendar_succeeded:
            do_update_display = True
            logger.info("systemsix.update_or_start(); got calendar this time.")

    if do_new_layout:
        new_layout()

    if do_update_display:
        update_display(period)


def update():
    logger.info("systemsix.update(); ========================================")
    update_or_start()


def main():
    # Initialize the display.
    # Set locale.
    locale.setlocale(locale.LC_ALL, LOCALE)

    # Update.
    update_or_start(True)
    
    # Schedule a call to update five minutes after every hour.
    schedule.every().hour.at("05:00").do(update)
    while True:
        schedule.run_pending()
        time.sleep(5)
    

if __name__ == '__main__':
    main()
