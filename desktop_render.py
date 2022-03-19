#!/usr/bin/python
import os
import logging
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple
from datetime import datetime
from icalevents.icalparser import Event
from moon_module import get_moon_phase


logger = logging.getLogger('app')


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
ARTWORK_DIR = os.path.join(CURRENT_DIR, 'artwork')
FONT_DIR = os.path.join(CURRENT_DIR, 'fonts')
FONT_CHICAGO = ImageFont.truetype(os.path.join(FONT_DIR, 'ChiKareGo2.ttf'), 16)
FONT_GENEVA_12 = ImageFont.truetype(os.path.join(FONT_DIR, 'Pixelva.ttf'), 16)
FONT_GENEVA_9 = ImageFont.truetype(os.path.join(FONT_DIR, 'geneva_9.ttf'), 16)


def title_image_for_index(index: int):
    if index == 0:
        return Image.open(os.path.join(ARTWORK_DIR, "art_window_title.bmp"))
    elif index == 1:
        return Image.open(os.path.join(ARTWORK_DIR, "dev_window_title.bmp"))
    elif index == 2:
        return Image.open(os.path.join(ARTWORK_DIR, "game_window_title.bmp"))
    elif index == 3:
        return Image.open(os.path.join(ARTWORK_DIR, "office_window_title.bmp"))
    elif index == 4:
        return Image.open(os.path.join(ARTWORK_DIR, "system_window_title.bmp"))
    else:
        return Image.open(os.path.join(ARTWORK_DIR, "util_window_title.bmp"))
        

# Map the moon phase to an image of the moon (0 to 24).
def moon_image_for_phase(phase: int):
    index = int((phase * 24) / 29)
    if index > 23:
        index = 0
    return index


def text_wrap(text, font, writing, max_width, max_height):
    lines = [[]]
    words = text.split()
    for one_word in words:
        # try putting this word in last line then measure
        lines[-1].append(one_word)
        (w,h) = writing.multiline_textsize('\n'.join([' '.join(line) for line in lines]), font=font)
        if w > max_width: # too wide
            # take it back out, put it on the next line, then measure again
            lines.append([lines[-1].pop()])
            (w,h) = writing.multiline_textsize('\n'.join([' '.join(line) for line in lines]), font=font)
            if h > max_height: # too high now, cannot fit this word in, so take out - add ellipses
                lines.pop()
                # try adding ellipses to last word fitting (i.e. without a space)
                lines[-1][-1] += '...'
                # keep checking that this doesn't make the textbox too wide,
                # if so, cycle through previous words until the ellipses can fit
                while writing.multiline_textsize('\n'.join([' '.join(line) for line in lines]),font=font)[0] > max_width:
                    lines[-1].pop()
                    if lines[-1]:
                        lines[-1][-1] += '...'
                    else:
                        lines[-1].append('...')
                break
    return '\n'.join([' '.join(line) for line in lines])


# Draw and image using a mask at the specified origin.
def draw_image_plus_mask(ink_image: Image, image_name: str, mask_name: str, origin: Tuple[int, ...]):
    image = Image.open(os.path.join(ARTWORK_DIR, image_name))
    mask = Image.open(os.path.join(ARTWORK_DIR, mask_name)).convert("L")
    ink_image.paste(image, origin, mask)


def image_with_icons(size: Tuple[int, ...], columns: int, rows: int, icons: Tuple[str, ...]):
    canvas = Image.new(mode = "RGBA", size = size, color='white')
    box_tall = int(size[1] / rows)

    # Draw icons from list.
    in_column = 0
    in_row = 0
    raised_index = -1
    for icon_name in icons:
        icon_image = Image.open(os.path.join(ARTWORK_DIR, icon_name))
        (icon_width, icon_height) = icon_image.size
        h_offset = int(((((in_column * 2) + 1) * size[0]) / (columns * 2)) - (icon_width / 2))
        v_offset = int(((in_row + 1) * size[1]) / rows) - icon_height
        v_offset -= int((box_tall - (icon_height + 12)) / 2)
        icon_mask = Image.open(os.path.join(ARTWORK_DIR, "icon_mask.bmp")).convert("L")
        (mask_width, mask_height) = icon_mask.size
        trim = int((mask_width - icon_width) / 2)
        cropped_mask = icon_mask.crop((trim, 0, icon_width + trim, icon_height))

        # Test for overlap with previously drawn icon.
        if (in_column > 0) and (h_offset < right_edge) and ((raised_index + 1) != in_column):
            raised_index = in_column
            v_offset -= 12

        canvas.paste(icon_image, (h_offset, v_offset), cropped_mask)
        # Record where the right edge of the icon landed (+padding).
        right_edge = h_offset + icon_width + 1
        in_column += 1
        if in_column >= columns:
            in_column = 0
            in_row = in_row + 1
            raised_index = -1

    return canvas


def draw_forecast(ink_draw: ImageDraw, origin: Tuple[int, ...], max_origin: Tuple[int, ...], forecast: list):
    v_offset = origin[1]
    max_width = max_origin[0] - origin[0]

    # Iterate over forecast periods.
    for period in forecast:
        # Test to see if we have exceeded our maximum vertical position. If so, we're done, we have run out of room.
        if v_offset > max_origin[1]:
            break

        height_delta = 14
        day_name = period['name']

        # Today's forecast is more robust, longer. Allow two lines of text.
        if period['number'] == 2:
            height_delta += 6
        if period['number'] <= 2:
            text = day_name + ": " + str(period['detailedForecast'])
            (text_wide, text_high) = ink_draw.multiline_textsize(text, font=FONT_GENEVA_9)
            if text_wide > max_width:
                text = text_wrap(text, FONT_GENEVA_9, ink_draw, max_width, 32)
                (text_wide, text_high) = ink_draw.multiline_textsize(text, font=FONT_GENEVA_9)
                height_delta += (int(text_high / 9) - 1) * 14
        else:
            text = day_name + ': ' + str(period['temperature']) + '\u00b0' + period['temperatureUnit'] + ', ' + \
                   period['shortForecast']
            (text_wide, text_high) = ink_draw.multiline_textsize(text, font=FONT_GENEVA_9)
            if text_wide > max_width:
                text = text_wrap(text, FONT_GENEVA_9, ink_draw, max_width, 12)
        ink_draw.text((origin[0], v_offset), text, font=FONT_GENEVA_9, fill=1)

        v_offset += height_delta

        # Draw a couple of horizontal lines to seperate today from future forecasts.
        if period['number'] == 2:
            ink_draw.line((origin[0], v_offset - 9, max_origin[0] - 5, v_offset - 9), fill=1, width=1)
            ink_draw.line((origin[0], v_offset - 7, max_origin[0] - 5, v_offset - 7), fill=1, width=1)


# Draw the desktop.
def draw_desktop(ink_image: Image, filename: str):
    desktop_image = Image.open(os.path.join(ARTWORK_DIR, filename))
    ink_image.paste(desktop_image, (20, 12))


# Draw the trash can empty or full.
def draw_trash(ink_image: Image, is_full: bool):
    if is_full:
        draw_image_plus_mask(ink_image, "trash_full.bmp", "trash_full_mask.bmp", (572, 410))
    else:
        draw_image_plus_mask(ink_image, "trash.bmp", "trash_mask.bmp", (572, 410))


# Draw the startup disk icon (either black or white).
def draw_startup_disk(ink_image: Image, is_black: bool):
    if is_black:
        draw_image_plus_mask(ink_image, "systemsix_disk_black.bmp", "systemsix_disk_mask.bmp", (562, 40))
    else:
        draw_image_plus_mask(ink_image, "systemsix_disk_white.bmp", "systemsix_disk_mask.bmp", (562, 40))


# Draw the paint window at the specified origin.
def draw_paint_window(ink_draw: ImageDraw, ink_image: Image, title_str: str):
    draw_image_plus_mask(ink_image, "paint_window.bmp", "paint_window_mask.bmp", (25, 37))

    # Draw date string passed in.
    if title_str is not None:
        (text_wide, text_high) = ink_draw.multiline_textsize(title_str, font=FONT_CHICAGO)
        x_offset = 25 + 270 - int(text_wide / 2)
        ink_draw.text((x_offset, 37 + 4), title_str, font=FONT_CHICAGO, fill=1)


# Draw the write window at the specified origin.
def draw_write_window(ink_draw: ImageDraw, ink_image: Image, title_str: str, forecast: list, enabled: bool):
    origin = (24, 36)
    if enabled:
        draw_image_plus_mask(ink_image, "write_window.bmp", "write_window_mask.bmp", origin)
    else:
        draw_image_plus_mask(ink_image, "write_window_disabled.bmp", "write_window_mask.bmp", origin)

    # Draw date string passed in.
    if title_str is not None:
        (text_wide, text_high) = ink_draw.multiline_textsize(title_str, font=FONT_CHICAGO)
        x_offset = 24 + 254 - int(text_wide / 2)
        ink_draw.rectangle((x_offset - 7, 36 + 1, x_offset + text_wide + 5, 36 + 17), fill="white")
        ink_draw.text((x_offset, 36 + 3), title_str, font=FONT_CHICAGO, fill=1)

    # Draw forecast.
    if forecast is not None:
        draw_forecast(ink_draw, (origin[0] + 12, origin[1] + 86), (origin[0] + 485, origin[1] + 280), forecast)


def draw_3_2_window(ink_image: Image, origin: Tuple[int, ...], index: int, icons: Tuple[str, ...], enabled: bool):
    if enabled:
        draw_image_plus_mask(ink_image, "window_3_2.bmp", "window_3_2_mask.bmp", origin)
    else:
        draw_image_plus_mask(ink_image, "window_3_2_disabled.bmp", "window_3_2_mask.bmp", origin)

    # Draw optional title bar image (maybe "Games" for example).
    title_image = title_image_for_index(index)
    if title_image is not None:
        (title_width, title_height) = title_image.size
        h_offset = origin[0] + int((226 - title_width) / 2)
        v_offset = origin[1] + 1
        ink_image.paste(title_image, (h_offset, v_offset))
    
    # Draw icons from list.
    icons_image = image_with_icons((208, 125), 3, 2, icons)
    ink_image.paste(icons_image, (origin[0] + 1, origin[1] + 39))


def draw_4_1_window(ink_image: Image, origin: Tuple[int, ...], icons: Tuple[str, ...], title_image: Image, enabled: bool):
    if enabled:
        draw_image_plus_mask(ink_image, "window_4_1.bmp", "window_4_1_mask.bmp", origin)
    else:
        draw_image_plus_mask(ink_image, "window_4_1_disabled.bmp", "window_4_1_mask.bmp", origin)

    # Draw optional title bar image (maybe "Games" for example).
    if title_image is not None:
        title_width, title_height = title_image.size
        h_offset = origin[0] + int((312 - title_width) / 2)
        v_offset = origin[1] + 1
        ink_image.paste(title_image, (h_offset, v_offset))

    # Draw icons.
    icons_image = image_with_icons((294, 82), 4, 1, icons)
    ink_image.paste(icons_image, (origin[0] + 1, origin[1] + 39))


def draw_list_window(ink_draw: ImageDraw, ink_image: Image, origin: Tuple[int, ...], event_list: List[Event]):
    draw_image_plus_mask(ink_image, "window_list_6.bmp", "window_list_6_mask.bmp", origin)

    # Indicate there are no calendar events.
    if (event_list is None) or (len(event_list) == 0):
        ink_draw.text((origin[0] + 144, origin[1] + 84), "No calendar events.", font=FONT_GENEVA_9, fill=1)
        return

    # Iterate over events in list and display them.
    v_offset = origin[1] + 44
    for event in event_list:
        # Draw tiny folder icon.
        folder = Image.open(os.path.join(ARTWORK_DIR, "folder_tiny.bmp"))
        ink_image.paste(folder, (origin[0] + 6, v_offset - 1))
        
        # Draw event description (title).
        ink_draw.text((origin[0] + 22, v_offset), event.summary, font=FONT_GENEVA_9, fill=1)
        
        # Draw event date.
        event_date = event.start.date()
        if datetime.now().date() != event_date:
            if event.all_day:
                ink_draw.text((origin[0] + 281, v_offset), event_date.strftime("%b %-d, (all day)"), font=FONT_GENEVA_9, fill=1)
            else:
                ink_draw.text((origin[0] + 281, v_offset), event.start.strftime("%b %-d, %-I:%M %p"), font=FONT_GENEVA_9, fill=1)
        else:
            if event.all_day:
                ink_draw.text((origin[0] + 281, v_offset), "(all day)", font=FONT_GENEVA_9, fill=1)
            else:
                ink_draw.text((origin[0] + 281, v_offset), event.start.strftime("%-I:%M %p"), font=FONT_GENEVA_9, fill=1)
        v_offset += 16
    

# Draw the Moon Phase "desk accessory" at the specified origin.
def draw_moon_da(ink_image: Image, origin: Tuple[int, ...], phase: int):
    draw_image_plus_mask(ink_image, "moon_da_window.bmp", "moon_da_window_mask.bmp", origin)

    # Load the moon image and draw.
    index = moon_image_for_phase(phase)
    filename = "moon" + str(index) + ".bmp"
    moon_image = Image.open(os.path.join(ARTWORK_DIR, filename))
    ink_image.paste(moon_image, (origin[0] + 1, origin[1] + 19))


def handle_display_moon(ink_image: Image, origin: Tuple[int, ...], today: datetime, period: str):
    # Only display the Moon desk accessory from evening to morning.
    if (period != "MIDNIGHT") and (period != "EVENING"):
        return False

    # Determine the current phase of the moon (0 to 29) and display it if not a new moon.
    # Otherwise, display either the Calculator or Puzzle desk accessory.
    user_date = (str(today.year) + "-" + str(today.month).zfill(2) + "-" + str(today.day).zfill(2))
    phase = get_moon_phase(user_date)
    index = moon_image_for_phase(phase)

    if (index > 0):
        draw_moon_da(ink_image, origin, phase)
        return True
    else:
        return False


# Draw the Puzzle "desk accessory" window at the specified origin.
def draw_puzzle_da(ink_image: Image, origin: Tuple[int, ...]):
    draw_image_plus_mask(ink_image, "puzzle.bmp", "puzzle_mask.bmp", origin)


# Draw the Calculator "desk accessory" window at the specified origin.
def draw_calculator_da(ink_image: Image, origin: Tuple[int, ...]):
    draw_image_plus_mask(ink_image, "calculator.bmp", "calculator_mask.bmp", origin)


# Draw the Key Caps "desk accessory" window at the specified origin.
def draw_key_caps_da(ink_draw: ImageDraw, ink_image: Image, origin: Tuple[int, ...], date_str: str):
    draw_image_plus_mask(ink_image, "key_caps.bmp", "key_caps_mask.bmp", origin)

    # Draw date string passed in.
    if date_str is not None:
        ink_draw.text((origin[0] + 46, origin[1] + 32), date_str, font=FONT_CHICAGO, fill=1)
    

# Draw the "Scrapbook" window at the specified origin.
def draw_scrapbook(ink_draw: ImageDraw, ink_image: Image, origin: Tuple[int, ...], date_str: str, adornments: Tuple[str, ...], forecast: list, enabled: bool):
    scrapbook_image_name = "scrapbook_disabled.bmp"
    if enabled:
        scrapbook_image_name = "scrapbook.bmp"
    scrapbook = Image.open(os.path.join(ARTWORK_DIR, scrapbook_image_name))
    scrapbook_mask = Image.open(os.path.join(ARTWORK_DIR, "scrapbook_mask.bmp")).convert("L")
    ink_image.paste(scrapbook, origin, scrapbook_mask)

    v_offset = 40

    # Draw date string passed in. Render twice (offset to right by one pixel) for bold.
    if date_str is not None:
        (text_wide, text_high) = ink_draw.multiline_textsize(date_str, font=FONT_GENEVA_12)
        ink_draw.text((origin[0] + 191 - int(text_wide / 2), origin[1] + 42), date_str, font=FONT_GENEVA_12, fill=1)
        ink_draw.text((origin[0] + 192 - int(text_wide / 2), origin[1] + 42), date_str, font=FONT_GENEVA_12, fill=1)

        v_offset = 65

    if forecast is None:
        memo_image = Image.open(os.path.join(ARTWORK_DIR, "memo.bmp"))
        ink_image.paste(memo_image, (origin[0] + 82, origin[1] + 93))
        return

    # Draw adornments passed in.
    if adornments is not None:
        left_adorn = Image.open(os.path.join(ARTWORK_DIR, adornments[0]))
        (image_width, image_height) = left_adorn.size
        ink_image.paste(left_adorn, (origin[0] + 40, origin[1] + 48 - int(image_height / 2)))

        right_adorn = Image.open(os.path.join(ARTWORK_DIR, adornments[1]))
        (image_width, image_height) = right_adorn.size
        ink_image.paste(right_adorn, (origin[0] + 344 - image_width, origin[1] + 48 - int(image_height / 2)))

        v_offset = 65

    # Draw forecast.
    draw_forecast(ink_draw, (origin[0] + 25, origin[1] + v_offset), (origin[0] + 365, origin[1] + 200), forecast)


# Draw the arrow cursor at origin.
# Good range for origin: x (20 to 630), y (16 to 450)
def draw_arrow_cursor(ink_image: Image, origin: Tuple[int, ...]):
    draw_image_plus_mask(ink_image, "arrow_cursor.bmp", "arrow_cursor_mask.bmp", origin)
